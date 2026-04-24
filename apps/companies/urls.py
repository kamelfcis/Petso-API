from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, CompanyAnalyticsViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'analytics', CompanyAnalyticsViewSet, basename='company-analytics')

urlpatterns = [
    path('', include(router.urls)),
]
