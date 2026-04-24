from django.contrib import admin
from .models import AdminAuditLog, SystemErrorLog, Notification, FutureFeature

@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'module', 'created_at')
    list_filter = ('module', 'created_at')
    search_fields = ('user__email', 'action', 'description')

@admin.register(SystemErrorLog)
class SystemErrorLogAdmin(admin.ModelAdmin):
    list_display = ('error_type', 'message_snippet', 'occurred_at', 'is_resolved')
    list_filter = ('error_type', 'is_resolved', 'occurred_at')
    search_fields = ('message', 'stack_trace')

    def message_snippet(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'priority', 'is_read', 'created_at')
    list_filter = ('type', 'priority', 'is_read', 'created_at')
    search_fields = ('user__email', 'title', 'body')

@admin.register(FutureFeature)
class FutureFeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'priority', 'status', 'created_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('name', 'description')
