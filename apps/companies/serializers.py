from rest_framework import serializers, viewsets, permissions
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

class CompanyAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CompanyAnalytics.objects.all()
    serializer_class = CompanyAnalyticsSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        if self.request.user.role == 'company':
            return self.queryset.filter(company__user=self.request.user)
        return self.queryset
