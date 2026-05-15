from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    UserViewSet,
    UserNotificationPreferenceViewSet,
    UserActivityLogViewSet,
    PetsoTokenObtainPairView,
    CurrentUserView,
    ConfirmEmailView,
    ResendConfirmationView,
)

router = DefaultRouter()
router.register(r'profile', UserViewSet, basename='user')
router.register(r'notifications', UserNotificationPreferenceViewSet, basename='notification-preference')
router.register(r'activity', UserActivityLogViewSet, basename='activity-log')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', PetsoTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm-email'),
    path('confirm-email/<str:token>/', ConfirmEmailView.as_view(), name='confirm-email-path'),
    path('resend-confirmation/', ResendConfirmationView.as_view(), name='resend-confirmation'),
]
