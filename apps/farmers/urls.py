from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FarmerProfileViewSet, PoultryFlockViewSet

router = DefaultRouter()
router.register(r'profile', FarmerProfileViewSet, basename='farmer-profile')
router.register(r'flocks', PoultryFlockViewSet, basename='poultry-flock')

urlpatterns = [
    path('', include(router.urls)),
]
