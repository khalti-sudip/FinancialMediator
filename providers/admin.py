"""Admin configuration for the providers app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Provider, ProviderKey, ProviderWebhook


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Admin interface for Provider model."""

    list_display = ["name", "code", "provider_type", "status", "created_at", "updated_at"]
    list_filter = ["status", "provider_type", "created_at", "updated_at"]
    search_fields = ["name", "code"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("name", "code", "provider_type", "status")}),
        (_("Configuration"), {"fields": ("base_url", "rate_limit", "webhook_url")}),
        (_("Audit Information"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ProviderKey)
class ProviderKeyAdmin(admin.ModelAdmin):
    """Admin interface for ProviderKey model."""

    list_display = ["provider", "key_id", "environment", "is_active", "created_at", "expires_at"]
    list_filter = ["provider", "environment", "is_active"]
    search_fields = ["key_id", "provider__name"]
    readonly_fields = ["key_id", "created_at", "last_used_at"]


@admin.register(ProviderWebhook)
class ProviderWebhookAdmin(admin.ModelAdmin):
    """Admin interface for ProviderWebhook model."""

    list_display = ["provider", "event_type", "status", "created_at", "processed_at"]
    list_filter = ["provider", "event_type", "status"]
    search_fields = ["event_id", "provider__name", "event_type"]
    readonly_fields = ["event_id", "created_at", "updated_at", "processed_at"]
    
    def has_change_permission(self, request, obj=None):
        # Webhooks should be immutable once created
        return False
