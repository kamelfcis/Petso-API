from django.db.models import Q
from rest_framework import serializers, viewsets, permissions
from .models import Chat, ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ChatMessage
        fields = '__all__'

class ChatSerializer(serializers.ModelSerializer):
    user1 = serializers.StringRelatedField(read_only=True)
    user2 = serializers.StringRelatedField(read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    class Meta:
        model = Chat
        fields = '__all__'

class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(Q(user1=self.request.user) | Q(user2=self.request.user))

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
