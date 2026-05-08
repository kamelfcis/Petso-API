from rest_framework import viewsets, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, UserNotificationPreference, UserActivityLog
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    UserNotificationPreferenceSerializer,
    UserActivityLogSerializer,
    PetsoTokenObtainPairSerializer,
)


class PetsoTokenObtainPairView(TokenObtainPairView):
    """JWT login that also returns user_id, email, name, and role."""
    serializer_class = PetsoTokenObtainPairSerializer

class CurrentUserView(APIView):
    """GET /api/auth/me/ — returns the logged-in user's profile."""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
