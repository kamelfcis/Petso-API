from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VetProfileViewSet, VetReviewViewSet

router = DefaultRouter()
router.register(r'profiles', VetProfileViewSet, basename='vet-profile')
router.register(r'reviews', VetReviewViewSet, basename='vet-review')

urlpatterns = [
    path('', include(router.urls)),
]
