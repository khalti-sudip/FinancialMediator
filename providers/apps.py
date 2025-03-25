"""Providers app configuration."""

from django.apps import AppConfig


class ProvidersConfig(AppConfig):
    """Configuration for the providers app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "providers"
    verbose_name = "Financial Service Providers"

    def ready(self):
        """Perform initialization tasks when the app is ready."""
        import providers.signals  # noqa
