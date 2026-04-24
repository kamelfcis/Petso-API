from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import NotificationViewSet, AdminAuditLogViewSet, SystemErrorLogViewSet, FutureFeatureViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'audit-logs', AdminAuditLogViewSet, basename='audit-log')
router.register(r'error-logs', SystemErrorLogViewSet, basename='error-log')
router.register(r'future-features', FutureFeatureViewSet, basename='future-feature')

urlpatterns = [
    path('', include(router.urls)),
]
