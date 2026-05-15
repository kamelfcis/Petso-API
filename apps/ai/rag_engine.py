"""
Poultry Disease RAG Engine
--------------------------
Uses Google Gemini (google-genai SDK) for embeddings + generation and
ChromaDB for vector storage.

Workflow:
  1. build_index()    – extract text from PDFs → embed → store in ChromaDB
  2. chat()           – retrieve relevant chunks → ask Gemini → return answer
  3. diagnose_image() – retrieve relevant chunks → send image + context to Gemini Vision
"""

import hashlib
import logging
from pathlib import Path

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

_EMBED_MODEL = "gemini-embedding-exp-03-07"
_GEN_MODEL = "gemini-2.0-flash"
_COLLECTION = "poultry_diseases"
_CHUNK_SIZE = 1500      # characters per chunk
_CHUNK_OVERLAP = 200    # overlap between consecutive chunks


def _split_text(text: str, size: int = _CHUNK_SIZE, overlap: int = _CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return [c.strip() for c in chunks if c.strip()]


class PoultryRAGEngine:
    """Singleton-friendly RAG engine – instantiate once per process."""

    def __init__(self, api_key: str, pdfs_dir: str | Path, db_dir: str | Path):
        self._client = genai.Client(api_key=api_key)
        self.pdfs_dir = Path(pdfs_dir)
        self.db_dir = Path(db_dir)
        self._collection = None

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _get_collection(self):
        if self._collection is None:
            import chromadb
            client = chromadb.PersistentClient(path=str(self.db_dir))
            self._collection = client.get_or_create_collection(
                name=_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    @staticmethod
    def _extract_pdf_chunks(pdf_path: Path) -> list[dict]:
        """Return list of {text, source, page} dicts from a PDF."""
        import pypdf
        chunks = []
        with open(pdf_path, "rb") as fh:
            reader = pypdf.PdfReader(fh)
            for page_num, page in enumerate(reader.pages, start=1):
                raw = page.extract_text() or ""
                if not raw.strip():
                    continue
                for chunk_text in _split_text(raw):
                    chunks.append(
                        {"text": chunk_text, "source": pdf_path.name, "page": page_num}
                    )
        return chunks

    def _embed(self, text: str, task: str = "RETRIEVAL_DOCUMENT") -> list[float]:
        response = self._client.models.embed_content(
            model=_EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type=task),
        )
        return response.embeddings[0].values

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def index_status(self) -> dict:
        """Return current index statistics."""
        try:
            col = self._get_collection()
            count = col.count()
            pdfs = list(self.pdfs_dir.glob("*.pdf"))
            return {
                "indexed_chunks": count,
                "pdf_files": [p.name for p in pdfs],
                "pdf_count": len(pdfs),
                "ready": count > 0,
            }
        except Exception as exc:
            return {"indexed_chunks": 0, "pdf_files": [], "pdf_count": 0, "ready": False, "error": str(exc)}

    def build_index(self) -> dict:
        """
        (Re)build the vector index from all PDFs in pdfs_dir.
        Returns {"chunks_indexed": N, "pdf_files": [...]}
        """
        pdf_files = sorted(self.pdfs_dir.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(
                f"No PDF files found in {self.pdfs_dir}. "
                "Upload your poultry disease PDFs to data/poultry_pdfs/ first."
            )

        col = self._get_collection()

        # Clear previous data
        existing = col.get()
        if existing["ids"]:
            col.delete(ids=existing["ids"])

        all_chunks: list[dict] = []
        for pdf_path in pdf_files:
            logger.info("Indexing %s …", pdf_path.name)
            all_chunks.extend(self._extract_pdf_chunks(pdf_path))

        if not all_chunks:
            raise ValueError("PDFs were found but no text could be extracted.")

        for chunk in all_chunks:
            chunk_id = hashlib.md5(
                f"{chunk['source']}|{chunk['page']}|{chunk['text'][:80]}".encode()
            ).hexdigest()
            embedding = self._embed(chunk["text"], task="RETRIEVAL_DOCUMENT")
            col.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[{"source": chunk["source"], "page": chunk["page"]}],
            )

        logger.info("Indexed %d chunks from %d PDF(s).", len(all_chunks), len(pdf_files))
        return {
            "chunks_indexed": len(all_chunks),
            "pdf_files": [p.name for p in pdf_files],
        }

    def retrieve_context(self, query: str, k: int = 5) -> list[dict]:
        """Retrieve top-k relevant chunks for a query."""
        col = self._get_collection()
        if col.count() == 0:
            return []
        n = min(k, col.count())
        q_embed = self._embed(query, task="RETRIEVAL_QUERY")
        results = col.query(query_embeddings=[q_embed], n_results=n)
        return [
            {"text": doc, "source": meta["source"], "page": meta["page"]}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]

    # ------------------------------------------------------------------ #
    #  Chat                                                                #
    # ------------------------------------------------------------------ #

    def chat(self, message: str, history: list[dict] | None = None) -> dict:
        """
        Answer a question about poultry diseases using RAG.

        history format:
            [{"role": "user", "content": "..."}, {"role": "model", "content": "..."}]

        Returns {"reply": str, "sources": list[dict]}
        """
        contexts = self.retrieve_context(message, k=6)
        context_block = "\n\n---\n\n".join(
            f"[{c['source']} – Page {c['page']}]\n{c['text']}" for c in contexts
        )

        system_instructions = (
            "أنت طبيب بيطري خبير متخصص في أمراض الدواجن. "
            "لديك مراجع علمية موثوقة عن أمراض الدواجن. "
            "أجب بدقة واحترافية، واستشهد بالمصدر إذا كان ذا صلة. "
            "إذا كان السؤال بالعربية فأجب بالعربية، وإذا كان بالإنجليزية فأجب بالإنجليزية.\n\n"
            "You are an expert veterinarian specialising in poultry diseases. "
            "Answer accurately and professionally, citing the reference when relevant. "
            "Reply in the same language as the question (Arabic or English).\n\n"
            f"Reference material:\n{context_block}"
        )

        # Build Gemini-compatible history
        gemini_history = []
        for h in (history or []):
            gemini_history.append(
                types.Content(
                    role=h["role"],
                    parts=[types.Part(text=h["content"])],
                )
            )

        chat_session = self._client.chats.create(
            model=_GEN_MODEL,
            config=types.GenerateContentConfig(system_instruction=system_instructions),
            history=gemini_history,
        )
        response = chat_session.send_message(message)

        return {
            "reply": response.text,
            "sources": [{"file": c["source"], "page": c["page"]} for c in contexts],
        }

    # ------------------------------------------------------------------ #
    #  Image diagnosis                                                     #
    # ------------------------------------------------------------------ #

    def diagnose_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        question: str | None = None,
    ) -> dict:
        """
        Diagnose a poultry disease from an image, augmented with RAG context.

        Returns {"diagnosis": str, "sources": list[dict]}
        """
        query = question or "ما هو المرض الظاهر في هذه الدجاجة؟ صف جميع الأعراض."
        contexts = self.retrieve_context(query, k=6)
        context_block = "\n\n---\n\n".join(
            f"[{c['source']} – Page {c['page']}]\n{c['text']}" for c in contexts
        )

        text_prompt = (
            "أنت طبيب بيطري خبير متخصص في أمراض الدواجن. "
            "استناداً إلى المراجع العلمية أدناه، قم بتحليل الصورة وأعطِ:\n"
            "1. اسم المرض أو الحالة الصحية المشتبه بها\n"
            "2. الأعراض الظاهرة في الصورة\n"
            "3. خيارات العلاج المقترحة\n"
            "4. إجراءات الوقاية\n"
            "5. مستوى الخطورة (خفيف / متوسط / شديد)\n\n"
            "You are an expert veterinarian specialising in poultry diseases. "
            "Analyse the image using the reference material below and provide:\n"
            "1. Suspected disease / condition name\n"
            "2. Visible symptoms\n"
            "3. Suggested treatment options\n"
            "4. Prevention measures\n"
            "5. Severity level (mild / moderate / severe)\n\n"
            f"Reference material:\n{context_block}\n\n"
        )

        if question:
            text_prompt += f"Additional question: {question}\n\n"

        text_prompt += (
            "Reply in Arabic if the additional question is in Arabic, otherwise reply in English. "
            "Structure your answer clearly with numbered sections."
        )

        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        response = self._client.models.generate_content(
            model=_GEN_MODEL,
            contents=[text_prompt, image_part],
        )

        return {
            "diagnosis": response.text,
            "sources": [{"file": c["source"], "page": c["page"]} for c in contexts],
        }
