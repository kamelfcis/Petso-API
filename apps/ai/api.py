from rest_framework import serializers, viewsets, permissions
from .models import AICase, AIDiagnosisLog, AIModelVersion

class AIModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelVersion
        fields = '__all__'

class AICaseSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = AICase
        fields = '__all__'
        read_only_fields = ('predicted_disease', 'confidence_score', 'status', 'submitted_at')

class AIDiagnosisLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDiagnosisLog
        fields = '__all__'

class AICaseViewSet(viewsets.ModelViewSet):
    queryset = AICase.objects.all()
    serializer_class = AICaseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
