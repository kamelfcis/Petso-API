from django.contrib import admin
from .models import Post, Comment, PostLike

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_snippet', 'status', 'created_at')
    search_fields = ('user__email', 'content')
    list_filter = ('status', 'created_at')
    actions = ('approve_posts', 'reject_posts')

    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    @admin.action(description="Approve selected posts")
    def approve_posts(self, request, queryset):
        queryset.update(status=Post.STATUS_APPROVED)

    @admin.action(description="Reject selected posts")
    def reject_posts(self, request, queryset):
        queryset.update(status=Post.STATUS_REJECTED)

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
