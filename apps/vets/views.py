from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

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
