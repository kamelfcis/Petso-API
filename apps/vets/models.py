from django.db import models
from django.conf import settings
from apps.farmers.models import FarmerProfile

class VetProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vet_profile')
    license_number = models.CharField(max_length=50, unique=True)
    license_document = models.FileField(upload_to='vets/licenses/', blank=True, null=True)
    specialties = models.CharField(max_length=255) # e.g., 'Poultry Specialist'
    qualifications = models.TextField()
    clinic_address = models.TextField()
    years_of_experience = models.IntegerField(default=0)
    available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.name}"

class VetReview(models.Model):
    vet = models.ForeignKey(VetProfile, on_delete=models.CASCADE, related_name='reviews')
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='vet_reviews')
    rating = models.IntegerField() # 1 to 5
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.vet} by {self.farmer}"
