from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api import AICaseViewSet
from .views import (
    PoultryDiagnoseView,
    PoultryChatView,
    PoultryChatHistoryView,
    PoultryChatSessionDetailView,
    PoultryBuildIndexView,
    PoultryIndexStatusView,
)

router = DefaultRouter()
router.register(r'cases', AICaseViewSet, basename='ai-case')

urlpatterns = [
    # Legacy AI cases
    path('', include(router.urls)),

    # ── Poultry disease RAG endpoints ────────────────────────────────────
    # POST  image + optional question → diagnosis
    path('poultry/diagnose/', PoultryDiagnoseView.as_view(), name='poultry-diagnose'),

    # POST  message + optional session_id → AI reply
    path('poultry/chat/', PoultryChatView.as_view(), name='poultry-chat'),

    # GET   list all sessions for the authenticated user
    path('poultry/chat/history/', PoultryChatHistoryView.as_view(), name='poultry-chat-history'),

    # GET   full message history for one session
    path('poultry/chat/<uuid:session_id>/', PoultryChatSessionDetailView.as_view(), name='poultry-chat-session'),

    # POST  (admin) rebuild vector index from PDFs
    path('poultry/build-index/', PoultryBuildIndexView.as_view(), name='poultry-build-index'),

    # GET   check index status
    path('poultry/index-status/', PoultryIndexStatusView.as_view(), name='poultry-index-status'),
]
