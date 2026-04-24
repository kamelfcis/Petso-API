from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, VerifyEmailView, UserViewSet, UserNotificationPreferenceViewSet, UserActivityLogViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'profile', UserViewSet, basename='user')
router.register(r'notifications', UserNotificationPreferenceViewSet, basename='notification-preference')
router.register(r'activity', UserActivityLogViewSet, basename='activity-log')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
