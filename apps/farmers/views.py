from rest_framework import viewsets, permissions
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

    def perform_create(self, serializer):
        # Automatically assign the logged-in user to this profile
        serializer.save(user=self.request.user)

class PoultryFlockViewSet(viewsets.ModelViewSet):
    queryset = PoultryFlock.objects.all()
    serializer_class = PoultryFlockSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(farmer__user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user's farmer profile to the flock
        farmer_profile = self.request.user.farmer_profile
        serializer.save(farmer=farmer_profile)
