"""
Provider Models Module.

This module defines models for:
- Payment providers
- Provider configurations
- API credentials
- Service status tracking
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class Provider(models.Model):
    """Model for managing payment service providers."""
    
    # Provider identifiers
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    
    # Provider type and capabilities
    provider_type = models.CharField(
        max_length=20,
        choices=[
            ("payment", "Payment Gateway"),
            ("wallet", "Digital Wallet"),
            ("bank", "Bank Integration"),
            ("kyc", "KYC Provider"),
        ],
    )
    supported_currencies = models.JSONField(default=list)
    supported_countries = models.JSONField(default=list)
    
    # Status and availability
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("online", "Online"),
            ("offline", "Offline"),
            ("maintenance", "Maintenance"),
            ("deprecated", "Deprecated"),
        ],
        default="online",
    )
    
    # API configuration
    api_base_url = models.URLField()
    api_version = models.CharField(max_length=10)
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=100, blank=True)
    
    # Rate limiting
    rate_limit = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Requests per minute",
    )
    concurrent_requests = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
    )
    
    # Credentials (encrypted)
    credentials = models.JSONField(
        default=dict,
        help_text="Encrypted API credentials",
    )
    
    # Configuration
    settings = models.JSONField(
        default=dict,
        help_text="Provider-specific settings",
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_check_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["provider_type"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.provider_type})"
    
    def check_status(self):
        """Check provider API status."""
        try:
            # Initialize client
            client = self.get_client()
            
            # Perform health check
            is_healthy = client.check_health()
            
            # Update status
            self.status = "online" if is_healthy else "offline"
            self.last_check_at = timezone.now()
            self.save(update_fields=["status", "last_check_at"])
            
            return is_healthy
            
        except Exception as e:
            self.status = "offline"
            self.last_check_at = timezone.now()
            self.save(update_fields=["status", "last_check_at"])
            return False

class ProviderKey(models.Model):
    """Model for managing provider API keys."""
    
    # Key details
    key_id = models.UUIDField(default=uuid.uuid4, unique=True)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    
    # Key status
    is_active = models.BooleanField(default=True)
    environment = models.CharField(
        max_length=20,
        choices=[
            ("sandbox", "Sandbox"),
            ("production", "Production"),
        ],
    )
    
    # Access control
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_keys",
    )
    
    # Usage limits
    daily_limit = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(1)],
    )
    monthly_limit = models.IntegerField(
        default=10000,
        validators=[MinValueValidator(1)],
    )
    
    # Key data (encrypted)
    key_data = models.JSONField(
        default=dict,
        help_text="Encrypted key data",
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        unique_together = [["provider", "user", "environment"]]
    
    def __str__(self):
        return f"{self.provider.name} - {self.environment}"
    
    def is_valid(self):
        """Check if key is valid and not expired."""
        if not self.is_active:
            return False
            
        if self.expires_at and timezone.now() >= self.expires_at:
            return False
            
        return True

class ProviderWebhook(models.Model):
    """Model for tracking provider webhook events."""
    
    # Event identifiers
    event_id = models.UUIDField(default=uuid.uuid4, unique=True)
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="webhooks",
    )
    
    # Event details
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    # Request details
    ip_address = models.GenericIPAddressField()
    headers = models.JSONField()
    signature = models.CharField(max_length=255)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["provider", "event_type"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.provider.name} - {self.event_type}"
    
    def verify_signature(self):
        """Verify webhook signature."""
        try:
            # Get provider secret
            secret = self.provider.webhook_secret
            
            # Calculate expected signature
            expected = calculate_signature(
                self.event_data,
                secret
            )
            
            # Compare signatures
            return self.signature == expected
            
        except Exception:
            return False
