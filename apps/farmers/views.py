from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import FarmerProfile, PoultryFlock
from .serializers import FarmerProfileSerializer, PoultryFlockSerializer

class FarmerProfileViewSet(viewsets.ModelViewSet):
    queryset = FarmerProfile.objects.all()
    serializer_class = FarmerProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    @action(
        detail=False,
        methods=["get"],
        url_path="all",
        permission_classes=(permissions.AllowAny,),
    )
    def list_all(self, request):
        """Public endpoint — returns all farmer profiles without authentication."""
        qs = FarmerProfile.objects.all().order_by("id")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # One profile per user (OneToOne). Re-POSTing must update, not insert — avoids UNIQUE on user_id.
        validated = dict(serializer.validated_data)
        validated.pop("user", None)
        profile, _created = FarmerProfile.objects.update_or_create(
            user=self.request.user,
            defaults=validated,
        )
        serializer.instance = profile

class PoultryFlockViewSet(viewsets.ModelViewSet):
    queryset = PoultryFlock.objects.all()
    serializer_class = PoultryFlockSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(farmer__user=self.request.user)

    def perform_create(self, serializer):
        # Serializer validates before this runs; `farmer` is optional so farmers need not send it.
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            farmer = serializer.validated_data.get("farmer")
            if farmer is None:
                raise ValidationError(
                    {"farmer": "This field is required when creating a flock as admin."}
                )
            serializer.save()
            return
        farmer_profile = FarmerProfile.objects.filter(user=user).first()
        if farmer_profile is None:
            raise ValidationError(
                {"farmer": "Create a farmer profile (POST /api/farmers/profile/) before adding flocks."}
            )
        serializer.save(farmer=farmer_profile)
