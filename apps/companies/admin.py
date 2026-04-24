from django.contrib import admin
from .models import Company, CompanyAnalytics

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contact_email', 'contact_phone', 'created_at')
    search_fields = ('name', 'user__email', 'contact_email')
    list_filter = ('created_at',)

@admin.register(CompanyAnalytics)
class CompanyAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('company', 'report_date', 'total_orders', 'total_revenue', 'total_products_sold')
    list_filter = ('report_date', 'company')
