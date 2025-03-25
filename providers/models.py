"""Models for the providers app."""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Provider(models.Model):
    """Model representing a financial service provider."""

    name = models.CharField(_("Name"), max_length=100)
    code = models.CharField(_("Code"), max_length=50, unique=True)
    api_key = models.CharField(_("API Key"), max_length=100, unique=True)
    api_secret = models.CharField(_("API Secret"), max_length=100)
    base_url = models.URLField(_("Base URL"))
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
        ],
        default="inactive",
    )
    rate_limit = models.IntegerField(_("Rate Limit (requests/minute)"), default=60)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_providers",
        verbose_name=_("Created By"),
    )

    class Meta:
        """Meta options for Provider model."""

        verbose_name = _("Provider")
        verbose_name_plural = _("Providers")
        ordering = ["name"]

    def __str__(self):
        """Return string representation of the provider."""
        return f"{self.name} ({self.code})"


class ProviderEndpoint(models.Model):
    """Model representing an endpoint for a provider."""

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="endpoints",
        verbose_name=_("Provider"),
    )
    name = models.CharField(_("Name"), max_length=100)
    path = models.CharField(_("Path"), max_length=200)
    method = models.CharField(
        _("HTTP Method"),
        max_length=10,
        choices=[
            ("GET", "GET"),
            ("POST", "POST"),
            ("PUT", "PUT"),
            ("PATCH", "PATCH"),
            ("DELETE", "DELETE"),
        ],
    )
    requires_auth = models.BooleanField(_("Requires Authentication"), default=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        """Meta options for ProviderEndpoint model."""

        verbose_name = _("Provider Endpoint")
        verbose_name_plural = _("Provider Endpoints")
        unique_together = ["provider", "path", "method"]
        ordering = ["provider", "name"]

    def __str__(self):
        """Return string representation of the endpoint."""
        return f"{self.provider.name} - {self.name} ({self.method})"


class ProviderCredential(models.Model):
    """Model for storing provider-specific credentials."""

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="credentials",
        verbose_name=_("Provider"),
    )
    key = models.CharField(_("Key"), max_length=100)
    value = models.CharField(_("Value"), max_length=500)
    is_encrypted = models.BooleanField(_("Is Encrypted"), default=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        """Meta options for ProviderCredential model."""

        verbose_name = _("Provider Credential")
        verbose_name_plural = _("Provider Credentials")
        unique_together = ["provider", "key"]
        ordering = ["provider", "key"]

    def __str__(self):
        """Return string representation of the credential."""
        return f"{self.provider.name} - {self.key}"

    def save(self, *args, **kwargs):
        """Override save to handle encryption."""
        if not self.is_encrypted and self.value:
            from django.conf import settings
            from cryptography.fernet import Fernet

            f = Fernet(settings.ENCRYPTION_KEY.encode())
            self.value = f.encrypt(self.value.encode()).decode()
            self.is_encrypted = True
        super().save(*args, **kwargs)

    def get_decrypted_value(self):
        """Get the decrypted value of the credential."""
        if self.is_encrypted and self.value:
            from django.conf import settings
            from cryptography.fernet import Fernet

            f = Fernet(settings.ENCRYPTION_KEY.encode())
            return f.decrypt(self.value.encode()).decode()
        return self.value
