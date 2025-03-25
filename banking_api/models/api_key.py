from django.db import models
from django.utils import timezone


class ApiKey(models.Model):
    """API key model for tracking external system credentials"""

    name = models.CharField(max_length=100, null=False)
    key_value = models.CharField(max_length=256, null=False)
    secret_value = models.CharField(max_length=256, null=True, blank=True)
    provider_type = models.CharField(max_length=50, null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "api_keys"
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return f"{self.name} - {self.provider_type}"

    def is_valid(self):
        """Check if the API key is still valid"""
        if not self.is_active:
            return False

        if self.expires_at and timezone.now() > self.expires_at:
            return False

        return True
