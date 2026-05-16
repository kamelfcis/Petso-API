from django.contrib import admin
from .models import VetProfile, VetReview

@admin.register(VetProfile)
class VetProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'specialties', 'is_admin_verified', 'available', 'rating', 'created_at')
    search_fields = ('user__name', 'license_number', 'specialties')
    list_filter = ('is_admin_verified', 'available', 'rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(VetReview)
class VetReviewAdmin(admin.ModelAdmin):
    list_display = ('vet', 'farmer', 'rating', 'created_at')
    search_fields = ('vet__user__name', 'farmer__user__name', 'review_text')
    list_filter = ('rating', 'created_at')
