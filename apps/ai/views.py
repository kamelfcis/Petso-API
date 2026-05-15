"""
Poultry Disease AI views
========================
Endpoints:
  POST /api/ai/poultry/diagnose/         – diagnose from image (+ optional question)
  POST /api/ai/poultry/chat/             – chat (text) with RAG chatbot
  GET  /api/ai/poultry/chat/history/     – list user's chat sessions
  GET  /api/ai/poultry/chat/<session_id>/– get full message history for a session
  POST /api/ai/poultry/build-index/      – (admin) rebuild vector index from PDFs
  GET  /api/ai/poultry/index-status/     – check index status
"""

import logging
import mimetypes

from django.conf import settings
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import PoultryDiagnosis, PoultryChatSession, PoultryChatMessage
from .rag_engine import PoultryRAGEngine

logger = logging.getLogger(__name__)

# ── Singleton engine ──────────────────────────────────────────────────────────
_engine: PoultryRAGEngine | None = None


def get_engine() -> PoultryRAGEngine:
    global _engine
    if _engine is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        _engine = PoultryRAGEngine(
            api_key=api_key,
            pdfs_dir=settings.POULTRY_PDFS_DIR,
            db_dir=settings.POULTRY_CHROMA_DIR,
        )
    return _engine


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_mime(image_file) -> str:
    """Guess MIME type from the uploaded file."""
    mime = getattr(image_file, 'content_type', None)
    if mime and mime.startswith('image/'):
        return mime
    guessed, _ = mimetypes.guess_type(image_file.name)
    return guessed or 'image/jpeg'


# ── Views ─────────────────────────────────────────────────────────────────────

class PoultryDiagnoseView(APIView):
    """
    POST /api/ai/poultry/diagnose/

    Multipart form fields:
      - image   (file, required)   – photo of the chicken
      - question (text, optional)  – e.g. "ما هذا المرض؟"

    Response:
      {
        "id": 1,
        "diagnosis": "...",
        "sources": [{"file": "...", "page": 1}, ...]
      }
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Diagnose poultry disease from image",
        description=(
            "Upload a photo of a sick chicken. The AI analyses the image using "
            "the poultry-disease knowledge base (RAG) and returns a structured diagnosis."
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"error": "يجب إرفاق صورة / 'image' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        question = request.data.get('question', '').strip()
        image_bytes = image_file.read()
        mime_type = _detect_mime(image_file)

        try:
            engine = get_engine()
            result = engine.diagnose_image(image_bytes, mime_type, question or None)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            logger.exception("diagnose_image failed")
            return Response(
                {"error": f"AI error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Rewind file for saving
        image_file.seek(0)
        diagnosis_obj = PoultryDiagnosis.objects.create(
            user=request.user,
            image=image_file,
            question=question,
            diagnosis=result["diagnosis"],
            sources=result["sources"],
        )

        return Response(
            {
                "id": diagnosis_obj.pk,
                "diagnosis": result["diagnosis"],
                "sources": result["sources"],
            }
        )


class PoultryChatView(APIView):
    """
    POST /api/ai/poultry/chat/

    JSON body:
      {
        "message":    "ما هي أعراض مرض نيوكاسل؟",
        "session_id": "uuid (optional – omit to start a new session)"
      }

    Response:
      {
        "session_id": "uuid",
        "reply":      "...",
        "sources":    [{"file": "...", "page": 1}, ...]
      }
    """
    parser_classes = [JSONParser, FormParser]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Chat with poultry disease AI chatbot",
        description=(
            "Send a question about poultry diseases. The AI uses the knowledge base "
            "(RAG) built from your PDF files and maintains conversation history per session."
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        message = (request.data.get('message') or '').strip()
        if not message:
            return Response(
                {"error": "يجب إرسال رسالة / 'message' field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_id = request.data.get('session_id', '').strip()

        # Resolve or create session
        if session_id:
            try:
                session = PoultryChatSession.objects.get(
                    session_id=session_id, user=request.user
                )
            except PoultryChatSession.DoesNotExist:
                return Response(
                    {"error": "Session not found or does not belong to you."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            session = PoultryChatSession.objects.create(
                user=request.user,
                title=message[:80],
            )

        # Build Gemini-compatible history from stored messages
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages.all()
        ]

        try:
            engine = get_engine()
            result = engine.chat(message, history=history)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            logger.exception("chat failed")
            return Response(
                {"error": f"AI error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Persist messages
        PoultryChatMessage.objects.create(
            session=session, role='user', content=message
        )
        PoultryChatMessage.objects.create(
            session=session,
            role='model',
            content=result["reply"],
            sources=result["sources"],
        )
        session.save()  # bump updated_at

        return Response(
            {
                "session_id": str(session.session_id),
                "reply": result["reply"],
                "sources": result["sources"],
            }
        )


class PoultryChatHistoryView(APIView):
    """
    GET /api/ai/poultry/chat/history/
    Returns the authenticated user's chat sessions (most recent first).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="List user's poultry chat sessions")
    def get(self, request):
        sessions = PoultryChatSession.objects.filter(user=request.user).values(
            'session_id', 'title', 'created_at', 'updated_at'
        )
        return Response(list(sessions))


class PoultryChatSessionDetailView(APIView):
    """
    GET /api/ai/poultry/chat/<session_id>/
    Returns the full message history for a specific session.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Get messages in a poultry chat session")
    def get(self, request, session_id):
        try:
            session = PoultryChatSession.objects.get(
                session_id=session_id, user=request.user
            )
        except PoultryChatSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        messages = session.messages.values('role', 'content', 'sources', 'created_at')
        return Response(
            {
                "session_id": str(session.session_id),
                "title": session.title,
                "messages": list(messages),
            }
        )


class PoultryBuildIndexView(APIView):
    """
    POST /api/ai/poultry/build-index/
    Admin-only. (Re)builds the vector index from PDFs in data/poultry_pdfs/.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="(Admin) Build / rebuild poultry RAG vector index",
        description=(
            "Reads all PDF files from data/poultry_pdfs/, extracts text, "
            "generates embeddings with Gemini, and persists them in ChromaDB. "
            "Must be called at least once before using diagnose or chat."
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
        try:
            engine = get_engine()
            result = engine.build_index()
        except FileNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            logger.exception("build_index failed")
            return Response(
                {"error": f"Index build error: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "success",
                "chunks_indexed": result["chunks_indexed"],
                "pdf_files": result["pdf_files"],
            }
        )


class PoultryIndexStatusView(APIView):
    """
    GET /api/ai/poultry/index-status/
    Returns current RAG index statistics.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="Check poultry RAG index status")
    def get(self, request):
        try:
            engine = get_engine()
            info = engine.index_status()
        except Exception as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(info)
