from rest_framework import serializers, viewsets, permissions
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
    class Meta:
        model = AppointmentSlot
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role == 'farmer':
            return self.queryset.filter(farmer__user=self.request.user)
        elif self.request.user.role == 'vet':
            return self.queryset.filter(vet__user=self.request.user)
        return self.queryset

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
