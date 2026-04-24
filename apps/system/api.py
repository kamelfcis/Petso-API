from rest_framework import serializers, viewsets, permissions
from .models import AdminAuditLog, SystemErrorLog, Notification, FutureFeature

class AdminAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminAuditLog
        fields = '__all__'

class SystemErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemErrorLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FutureFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FutureFeature
        fields = '__all__'

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdminAuditLog.objects.all()
    serializer_class = AdminAuditLogSerializer
    permission_classes = (permissions.IsAdminUser,)

class SystemErrorLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemErrorLog.objects.all()
    serializer_class = SystemErrorLogSerializer
    permission_classes = (permissions.IsAdminUser,)

class FutureFeatureViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FutureFeature.objects.all()
    serializer_class = FutureFeatureSerializer
    permission_classes = (permissions.AllowAny,)
