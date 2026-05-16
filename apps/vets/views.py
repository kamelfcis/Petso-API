from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VetProfile, VetReview
from .serializers import (
    VetProfileSerializer,
    VetReviewSerializer,
    VetRegistrationSerializer,
    VetRegistrationResponseSerializer,
)
from apps.users.email_utils import send_confirmation_email

class VetProfileViewSet(viewsets.ModelViewSet):
    queryset = VetProfile.objects.all().order_by('id')
    serializer_class = VetProfileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'vet':
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=(permissions.AllowAny,),
    )
    def list_all(self, request):
        """Public endpoint — returns all vet profiles without authentication."""
        qs = VetProfile.objects.all().order_by("id")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = VetProfile.objects.count()
        VetProfile.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)

class VetReviewViewSet(viewsets.ModelViewSet):
    queryset = VetReview.objects.select_related("vet__user", "farmer__user").all()
    serializer_class = VetReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = VetReview.objects.count()
        VetReview.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)


class VetRegistrationView(generics.CreateAPIView):
    """POST /api/vets/register/ — Register a new vet with license PDF upload."""
    serializer_class = VetRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        vet_profile = serializer.save()
        user = vet_profile.user
        # Send confirmation email to the vet
        sent = send_confirmation_email(user)
        if not sent:
            # Email delivery failed — auto-verify email so vet isn't locked out
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])
            vet_profile._email_sent = False
        else:
            vet_profile._email_sent = True

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        vet_profile = serializer.instance
        response_serializer = VetRegistrationResponseSerializer(vet_profile)

        message = (
            "Registration successful. Please check your email to confirm your account. "
            "Your account will be pending admin verification."
        )

        if vet_profile and getattr(vet_profile, "_email_sent", True) is False:
            message = (
                "Registration successful. Email confirmation could not be sent right now — "
                "you can use resend-confirmation later. Your account is pending admin verification."
            )

        response_data = response_serializer.data
        response_data["message"] = message

        return Response(response_data, status=status.HTTP_201_CREATED)


class VetVerificationListView(generics.ListAPIView):
    """GET /api/vets/pending-verification/ — List all vets pending admin verification."""
    serializer_class = VetProfileSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = VetProfile.objects.filter(is_admin_verified=False).select_related('user').order_by('-created_at')


class AdminVerifyVetView(APIView):
    """POST /api/vets/{vet_id}/admin-verify/ — Admin verifies/confirms a vet."""
    permission_classes = (permissions.IsAdminUser,)

    def post(self, request, vet_id):
        try:
            vet_profile = VetProfile.objects.get(id=vet_id)
        except VetProfile.DoesNotExist:
            return Response(
                {"detail": "Vet profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if vet_profile.is_admin_verified:
            return Response(
                {"detail": "This vet is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vet_profile.is_admin_verified = True
        vet_profile.save(update_fields=["is_admin_verified"])

        return Response({
            "detail": "Vet verified successfully.",
            "vet_id": vet_profile.id,
            "user_email": vet_profile.user.email,
            "user_name": vet_profile.user.name,
            "is_admin_verified": vet_profile.is_admin_verified,
        }, status=status.HTTP_200_OK)


class AdminRejectVetView(APIView):
    """DELETE /api/vets/{vet_id}/admin-reject/ — Admin rejects/deletes a vet registration."""
    permission_classes = (permissions.IsAdminUser,)

    def delete(self, request, vet_id):
        try:
            vet_profile = VetProfile.objects.get(id=vet_id)
        except VetProfile.DoesNotExist:
            return Response(
                {"detail": "Vet profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = vet_profile.user
        user_email = user.email
        vet_profile.delete()
        user.delete()

        return Response({
            "detail": "Vet registration rejected and deleted.",
            "user_email": user_email,
        }, status=status.HTTP_200_OK)
