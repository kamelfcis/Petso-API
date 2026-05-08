from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, CompanyAnalytics

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class CompanyAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAnalytics
        fields = '__all__'

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["delete"], url_path="delete-all",
            permission_classes=(permissions.IsAdminUser,))
    def delete_all(self, request):
        n = Company.objects.count()
        Company.objects.all().delete()
        return Response({"deleted": n}, status=status.HTTP_200_OK)

class CompanyAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CompanyAnalytics.objects.all()
    serializer_class = CompanyAnalyticsSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        if self.request.user.role == 'company':
            return self.queryset.filter(company__user=self.request.user)
        return self.queryset
