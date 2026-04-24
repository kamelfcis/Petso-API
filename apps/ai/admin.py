from django.contrib import admin
from .models import AICase, AIDiagnosisLog, AIModelVersion

@admin.register(AIModelVersion)
class AIModelVersionAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'version', 'accuracy_score', 'is_active', 'deployed_at')
    list_filter = ('is_active', 'deployed_at')

@admin.register(AICase)
class AICaseAdmin(admin.ModelAdmin):
    list_display = ('Title', 'user', 'animal_type', 'predicted_disease', 'confidence_score', 'status', 'submitted_at')
    list_filter = ('animal_type', 'status', 'submitted_at')
    search_fields = ('Title', 'user__email', 'predicted_disease')

@admin.register(AIDiagnosisLog)
class AIDiagnosisLogAdmin(admin.ModelAdmin):
    list_display = ('ai_case', 'user', 'predicted_disease', 'confidence_score', 'processing_time_ms', 'created_at')
    list_filter = ('created_at',)
