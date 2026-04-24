from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, OrderDiscount

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'company', 'status', 'total', 'payment_method', 'delivery_date', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__email', 'company__name')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = ('order_number', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status', 'created_at')

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('changed_at',)
