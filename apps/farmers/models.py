from django.db import models
from django.conf import settings

class FarmerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=255)
    farm_location = models.TextField()
    farm_address = models.TextField(blank=True, null=True)
    farm_area = models.DecimalField(max_digits=10, decimal_places=2, help_text='Area in acres/hectares')
    flock_size = models.IntegerField(default=0)
    farm_type = models.CharField(max_length=100) # e.g., 'Broiler', 'Layer'
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    gps_long = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.farm_name

class PoultryFlock(models.Model):
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='flocks')
    flock_name = models.CharField(max_length=255)
    breed = models.CharField(max_length=100)
    hatch_date = models.DateField()
    current_age_weeks = models.IntegerField(default=0)
    total_count = models.IntegerField()
    mortality_count = models.IntegerField(default=0)
    feed_consumption = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flock_name} ({self.breed})"
