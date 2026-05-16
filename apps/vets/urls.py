from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VetProfileViewSet,
    VetReviewViewSet,
    VetRegistrationView,
    VetVerificationListView,
    AdminVerifyVetView,
    AdminRejectVetView,
)

router = DefaultRouter()
router.register(r'profiles', VetProfileViewSet, basename='vet-profile')
router.register(r'reviews', VetReviewViewSet, basename='vet-review')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', VetRegistrationView.as_view(), name='vet-register'),
    path('pending-verification/', VetVerificationListView.as_view(), name='pending-vets'),
    path('<int:vet_id>/admin-verify/', AdminVerifyVetView.as_view(), name='admin-verify-vet'),
    path('<int:vet_id>/admin-reject/', AdminRejectVetView.as_view(), name='admin-reject-vet'),
]
