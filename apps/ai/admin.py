from django.contrib import admin
from .models import AICase, AIDiagnosisLog, AIModelVersion, PoultryDiagnosis, PoultryChatSession, PoultryChatMessage


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


@admin.register(PoultryDiagnosis)
class PoultryDiagnosisAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'question', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'diagnosis')
    readonly_fields = ('diagnosis', 'sources', 'created_at')


class PoultryChatMessageInline(admin.TabularInline):
    model = PoultryChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'sources', 'created_at')
    can_delete = False


@admin.register(PoultryChatSession)
class PoultryChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__email', 'title')
    readonly_fields = ('session_id',)
    inlines = [PoultryChatMessageInline]
