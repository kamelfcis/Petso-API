from django.db import models
from django.conf import settings
from apps.farmers.models import FarmerProfile, PoultryFlock
from apps.vets.models import VetProfile

class ServiceRequest(models.Model):
    SERVICE_TYPES = (
        ('consultation', 'Consultation'),
        ('emergency', 'Emergency'),
        ('vaccination', 'Vaccination'),
        ('surgery', 'Surgery'),
    )

    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='service_requests')
    vet = models.ForeignKey(VetProfile, on_delete=models.SET_NULL, null=True, related_name='service_requests')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_type} for {self.farmer}"

class Prescription(models.Model):
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name='prescriptions_written')
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='prescriptions_received')
    flock = models.ForeignKey(PoultryFlock, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    diagnosis = models.TextField()
    prescription_text = models.TextField()
    status = models.CharField(max_length=20, default='active')
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription {self.id} for {self.farmer}"

class AppointmentSlot(models.Model):
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.vet} on {self.date} at {self.start_time}"

class Appointment(models.Model):
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='appointments')
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name='appointments')
    slot = models.OneToOneField(AppointmentSlot, on_delete=models.SET_NULL, null=True, related_name='appointment')
    status = models.CharField(max_length=20, default='scheduled')
    scheduled_start = models.DateTimeField()
    scheduled_end = models.DateTimeField()

    def __str__(self):
        return f"Appt {self.id} - {self.farmer} with {self.vet}"

class AppointmentStatusHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
