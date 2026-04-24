from django.db import models
from django.conf import settings

class AdminAuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"

class SystemErrorLog(models.Model):
    error_type = models.CharField(max_length=100)
    message = models.TextField()
    stack_trace = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    occurred_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

class Notification(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=50) # e.g., 'order', 'system', 'chat'
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class FutureFeature(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
