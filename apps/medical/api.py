from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.vets.models import VetProfile
from .models import ServiceRequest, Prescription, AppointmentSlot, Appointment, AppointmentStatusHistory


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'


class AppointmentSlotSerializer(serializers.ModelSerializer):
    """`vet` is set automatically from the JWT for role=vet; include it for admin/read."""

    class Meta:
        model = AppointmentSlot
        fields = '__all__'
        extra_kwargs = {
            "vet": {"required": False},
        }


class AppointmentSerializer(serializers.ModelSerializer):
    vet_name = serializers.CharField(source="vet.user.name", read_only=True)
    farmer_name = serializers.CharField(source="farmer.user.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "farmer",
            "farmer_name",
            "vet",
            "vet_name",
            "slot",
            "status",
            "scheduled_start",
            "scheduled_end",
        )


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    """
    Vets manage their own slots.
    Anyone (including unauthenticated) can list/read slots.
    Filter: ?vet=<vet_profile_id>  ?is_available=true  ?date=YYYY-MM-DD
    """
    queryset = AppointmentSlot.objects.all().order_by("date", "start_time")
    serializer_class = AppointmentSlotSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def _vet_profile(self):
        profile = VetProfile.objects.filter(user=self.request.user).first()
        if profile is None:
            raise ValidationError(
                {"vet": "Create a vet profile (POST /api/vets/profiles/) before managing slots."}
            )
        return profile

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        # Filter by vet user_id (User table PK), not VetProfile PK
        vet_id = params.get("vet")
        if vet_id:
            qs = qs.filter(vet__user_id=vet_id)

        is_available = params.get("is_available")
        if is_available is not None:
            qs = qs.filter(is_available=is_available.lower() in ("true", "1", "yes"))

        date = params.get("date")
        if date:
            qs = qs.filter(date=date)

        # Vets see only their own slots on write actions; list is unrestricted
        user = self.request.user
        if self.action not in ("list", "retrieve") and user.is_authenticated and getattr(user, "role", None) == "vet":
            profile = VetProfile.objects.filter(user=user).first()
            if profile:
                qs = qs.filter(vet=profile)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, "role", None) != "vet" and not user.is_staff:
            raise ValidationError({"detail": "Only vets (or staff) can create appointment slots."})
        vet_profile = self._vet_profile() if not user.is_staff else serializer.validated_data.get("vet")
        if user.is_staff:
            serializer.save()
        else:
            serializer.save(vet=vet_profile)

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_staff and getattr(user, "role", None) == "vet":
            if serializer.instance.vet != VetProfile.objects.filter(user=user).first():
                raise ValidationError({"detail": "You can only edit your own slots."})
        serializer.save()

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = AppointmentSlot.objects.count()
        AppointmentSlot.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related(
        "vet", "vet__user", "farmer", "farmer__user", "slot"
    )
    serializer_class = AppointmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    ALLOWED_STATUSES = ("scheduled", "accepted", "finished", "rejected", "cancelled")
    VET_ALLOWED_STATUSES = ("accepted", "finished", "rejected")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'farmer':
            return qs.filter(farmer__user=self.request.user)
        elif self.request.user.role == 'vet':
            return qs.filter(vet__user=self.request.user)
        return qs

    @action(detail=True, methods=["patch"], url_path="update-status",
            permission_classes=(permissions.IsAuthenticated,))
    def update_status(self, request, pk=None):
        """Vet updates appointment status to accepted / finished / rejected."""
        appointment = self.get_object()
        user = request.user

        if getattr(user, "role", None) != "vet" and not user.is_staff:
            return Response(
                {"detail": "Only vets (or staff) can update appointment status."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.is_staff:
            vet_profile = VetProfile.objects.filter(user=user).first()
            if vet_profile is None or appointment.vet != vet_profile:
                return Response(
                    {"detail": "You can only update status for your own appointments."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        new_status = request.data.get("status", "").strip()
        allowed = self.VET_ALLOWED_STATUSES if not user.is_staff else self.ALLOWED_STATUSES
        if new_status not in allowed:
            return Response(
                {"detail": f"Invalid status. Allowed values: {', '.join(allowed)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = new_status
        appointment.save(update_fields=["status"])
        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = Appointment.objects.count()
        Appointment.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'farmer':
            return self.queryset.filter(farmer__user=self.request.user)
        elif self.request.user.role == 'vet':
            return self.queryset.filter(vet__user=self.request.user)
        return self.queryset

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = Prescription.objects.count()
        Prescription.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)
