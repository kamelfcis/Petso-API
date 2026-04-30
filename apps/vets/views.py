from rest_framework import viewsets, permissions
from .models import VetProfile, VetReview
from .serializers import VetProfileSerializer, VetReviewSerializer

class VetProfileViewSet(viewsets.ModelViewSet):
    queryset = VetProfile.objects.all().order_by('id')
    serializer_class = VetProfileSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'vet':
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        # user is read-only on VetProfileSerializer; must bind the logged-in vet here
        serializer.save(user=self.request.user)

class VetReviewViewSet(viewsets.ModelViewSet):
    queryset = VetReview.objects.all()
    serializer_class = VetReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        # Ensure farmer is the one creating review
        # farmer = FarmerProfile.objects.get(user=self.request.user)
        serializer.save()
