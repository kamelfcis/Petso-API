from django.contrib import admin
from .models import ServiceRequest, Prescription, AppointmentSlot, Appointment, AppointmentStatusHistory

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'vet', 'service_type', 'status', 'requested_at')
    list_filter = ('service_type', 'status', 'requested_at')
    search_fields = ('farmer__user__name', 'vet__user__name')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'vet', 'farmer', 'status', 'issued_date')
    list_filter = ('status', 'issued_date')
    search_fields = ('vet__user__name', 'farmer__user__name', 'diagnosis')

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ('vet', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available', 'vet')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'vet', 'status', 'scheduled_start')
    list_filter = ('status', 'scheduled_start')
    search_fields = ('farmer__user__name', 'vet__user__name')

@admin.register(AppointmentStatusHistory)
class AppointmentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'status', 'changed_at')
