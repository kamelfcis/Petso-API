from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import AICaseViewSet

router = DefaultRouter()
router.register(r'cases', AICaseViewSet, basename='ai-case')

urlpatterns = [
    path('', include(router.urls)),
]
