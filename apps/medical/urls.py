from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import AppointmentViewSet, AppointmentSlotViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'slots', AppointmentSlotViewSet, basename='appointment-slot')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
]
