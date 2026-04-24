from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ChatViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(r'chats', ChatViewSet, basename='chat')
router.register(r'messages', ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
]
