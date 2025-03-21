
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from banking_api.models.kyc import KYCProfile, DematAccount
from banking_api.models.user import User
from banking_api.models.transaction import Transaction
from banking_api.models.audit_log import AuditLog

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'date_joined', 'is_active')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

@admin.register(KYCProfile)
class KYCProfileAdmin(ModelAdmin):
    list_display = ('user', 'mobile_number', 'full_name', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__username', 'mobile_number', 'full_name')
    ordering = ('-created_at',)

@admin.register(DematAccount)
class DematAccountAdmin(ModelAdmin):
    list_display = ('id', 'user', 'status', 'balance_display')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username')
    
    def balance_display(self, obj):
        color = 'green' if obj.balance > 0 else 'red'
        return format_html('<span style="color: {}">₹ {:,.2f}</span>', color, obj.balance)
    balance_display.short_description = 'Balance'

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('id', 'customer', 'amount_display', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('customer__username', 'reference_id')
    readonly_fields = ('created_at',)
    
    def amount_display(self, obj):
        color = 'green' if obj.transaction_type == 'CREDIT' else 'red'
        return format_html('<span style="color: {}">₹ {:,.2f}</span>', color, obj.amount)
    amount_display.short_description = 'Amount'

@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ('action', 'user', 'resource_type', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('user__username', 'resource_id')
    readonly_fields = ('created_at',)

# Customize admin site
admin.site.site_header = 'Banking Middleware Administration'
admin.site.site_title = 'Banking Admin Portal'
admin.site.index_title = 'Welcome to Banking Middleware Portal'
