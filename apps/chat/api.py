from django.db.models import Q
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.response import Response

from apps.users.models import User
from .models import Chat, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    user1_email = serializers.EmailField(source='user1.email', read_only=True)
    user2_email = serializers.EmailField(source='user2.email', read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'user1', 'user1_email', 'user2', 'user2_email', 'messages', 'created_at')
        read_only_fields = ('user1',)


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Chat.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).select_related('user1', 'user2').order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user1=self.request.user)

    def create(self, request, *args, **kwargs):
        """Return existing chat if one already exists between these two users (in either direction)."""
        user2_id = request.data.get('user2')
        if user2_id:
            existing = Chat.objects.filter(
                Q(user1=request.user, user2_id=user2_id) |
                Q(user1_id=user2_id, user2=request.user)
            ).first()
            if existing:
                serializer = self.get_serializer(existing)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ChatMessage.objects.filter(
            Q(chat__user1=self.request.user) | Q(chat__user2=self.request.user)
        ).select_related('sender').order_by('created_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
