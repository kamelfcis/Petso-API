from rest_framework import viewsets, permissions, status
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
