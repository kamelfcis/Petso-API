from django.contrib import admin
from .models import Post, Comment, PostLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_snippet', 'created_at')
    search_fields = ('user__email', 'content')
    list_filter = ('created_at',)

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content_snippet', 'created_at')
    list_filter = ('created_at',)

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
