from django.core import signing

from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .email_utils import send_confirmation_email, verify_confirmation_token
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

    def perform_create(self, serializer):
        user = serializer.save()
        sent = send_confirmation_email(user)
        if not sent:
            # Email delivery failed (e.g. rate limit). Auto-verify so the user
            # is not permanently locked out. They can still use resend later.
            user.is_email_verified = True
            user.is_verified = True
            user.save(update_fields=["is_email_verified", "is_verified"])
            # Store flag on instance so create() can adjust response message
            user._email_sent = False
        else:
            user._email_sent = True

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Access the created user to check if email was sent
        user = User.objects.filter(email=request.data.get("email", "")).first()
        if user and getattr(user, "_email_sent", True) is False:
            response.data["message"] = (
                "Registration successful. Email confirmation could not be sent right now — "
                "you can log in directly or use resend-confirmation later."
            )
        else:
            response.data["message"] = (
                "Registration successful. Please check your email to confirm your account."
            )
        return response


class ConfirmEmailView(APIView):
    """GET /api/auth/confirm-email/?token=<token>"""
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response(
                {"detail": "Invalid or expired confirmation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_pk = verify_confirmation_token(token)
        except signing.SignatureExpired:
            return Response(
                {"detail": "Invalid or expired confirmation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except signing.BadSignature:
            return Response(
                {"detail": "Invalid or expired confirmation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired confirmation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_email_verified:
            return Response(
                {"message": "Email already confirmed. You can log in."},
                status=status.HTTP_200_OK,
            )

        user.is_email_verified = True
        user.is_verified = True
        user.save(update_fields=["is_email_verified", "is_verified"])

        return Response(
            {"message": "Email confirmed successfully. You can now log in."},
            status=status.HTTP_200_OK,
        )


class ResendConfirmationView(APIView):
    """POST /api/auth/resend-confirmation/  body: { "email": "..." }"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response(
                {"detail": "email field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Always return the same response to avoid user enumeration
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"message": "If that email exists and is unverified, a new confirmation link has been sent."},
                status=status.HTTP_200_OK,
            )

        if user.is_email_verified:
            return Response(
                {"message": "This email is already confirmed. You can log in."},
                status=status.HTTP_200_OK,
            )

        send_confirmation_email(user)
        return Response(
            {"message": "If that email exists and is unverified, a new confirmation link has been sent."},
            status=status.HTTP_200_OK,
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = User.objects.count()
        User.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)


class UserNotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserNotificationPreference.objects.all()
    serializer_class = UserNotificationPreferenceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = UserNotificationPreference.objects.count()
        UserNotificationPreference.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)


class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = UserActivityLog.objects.count()
        UserActivityLog.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)
