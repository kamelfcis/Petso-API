from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'user', 'amount', 'method', 'status', 'order', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('transaction_reference', 'user__email', 'order__order_number')
    readonly_fields = ('transaction_reference', 'created_at')
