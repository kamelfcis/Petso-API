from django.contrib import admin
from .models import Chat, ChatMessage

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'created_at')
    search_fields = ('user1__email', 'user2__email')
    list_filter = ('created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'message_snippet', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'message')

    def message_snippet(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
