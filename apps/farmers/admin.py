from django.contrib import admin
from .models import FarmerProfile, PoultryFlock

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'farm_area', 'flock_size', 'farm_type', 'created_at')
    search_fields = ('user__name', 'farm_name')
    list_filter = ('farm_type', 'created_at')

@admin.register(PoultryFlock)
class PoultryFlockAdmin(admin.ModelAdmin):
    list_display = ('flock_name', 'farmer', 'breed', 'total_count', 'mortality_count', 'hatch_date')
    search_fields = ('flock_name', 'farmer__farm_name')
    list_filter = ('breed', 'hatch_date')
