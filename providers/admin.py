"""Admin configuration for the providers app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Provider, ProviderEndpoint, ProviderCredential


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    """Admin interface for Provider model."""

    list_display = ["name", "code", "status", "rate_limit", "created_at", "updated_at"]
    list_filter = ["status", "created_at", "updated_at"]
    search_fields = ["name", "code"]
    readonly_fields = ["created_at", "updated_at", "created_by"]
    fieldsets = (
        (None, {"fields": ("name", "code", "base_url", "status")}),
        (_("API Configuration"), {"fields": ("api_key", "api_secret", "rate_limit")}),
        (
            _("Audit Information"),
            {"fields": ("created_by", "created_at", "updated_at")},
        ),
    )

    def save_model(self, request, obj, form, change):
        """Save model with created_by user."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProviderEndpoint)
class ProviderEndpointAdmin(admin.ModelAdmin):
    """Admin interface for ProviderEndpoint model."""

    list_display = ["provider", "name", "path", "method", "is_active"]
    list_filter = ["provider", "method", "is_active", "requires_auth"]
    search_fields = ["name", "path", "provider__name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(ProviderCredential)
class ProviderCredentialAdmin(admin.ModelAdmin):
    """Admin interface for ProviderCredential model."""

    list_display = ["provider", "key", "is_encrypted", "created_at", "updated_at"]
    list_filter = ["provider", "is_encrypted"]
    search_fields = ["provider__name", "key"]
    readonly_fields = ["created_at", "updated_at", "is_encrypted"]
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of existing credentials for security."""
        return obj is None
