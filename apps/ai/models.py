from django.db import models
from django.conf import settings

class AIModelVersion(models.Model):
    model_name = models.CharField(max_length=255)
    version = models.CharField(max_length=50)
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=4)
    is_active = models.BooleanField(default=True)
    deployed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_name} v{self.version}"

class AICase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_cases')
    Title = models.CharField(max_length=255)
    symptoms = models.TextField()
    images = models.JSONField() # Store image URLs or metadata
    animal_type = models.CharField(max_length=100)
    predicted_disease = models.CharField(max_length=255, blank=True, null=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Title

class AIDiagnosisLog(models.Model):
    ai_case = models.ForeignKey(AICase, on_delete=models.CASCADE, related_name='diagnosis_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_diagnosis_logs')
    ai_model_version = models.ForeignKey(AIModelVersion, on_delete=models.SET_NULL, null=True)
    input_type = models.CharField(max_length=50) # image/text
    confidence_score = models.DecimalField(max_digits=5, decimal_places=4)
    predicted_disease = models.CharField(max_length=255)
    processing_time_ms = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
