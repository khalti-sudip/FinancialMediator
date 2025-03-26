"""
KYC Service Models.

This module defines models for KYC (Know Your Customer) verification.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid


class KYCProvider(models.Model):
    """
    Model for managing KYC verification providers.
    
    Each provider can have different verification methods and requirements.
    """
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    
    # Provider capabilities
    supports_document_verification = models.BooleanField(default=True)
    supports_face_verification = models.BooleanField(default=True)
    supports_address_verification = models.BooleanField(default=True)
    supports_background_check = models.BooleanField(default=True)
    
    # API configuration
    api_base_url = models.URLField()
    api_version = models.CharField(max_length=10)
    webhook_url = models.URLField(blank=True)
    webhook_secret = models.CharField(max_length=100, blank=True)
    
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
    
    # Rate limiting
    rate_limit = models.IntegerField(
        default=100,
        validators=[MinValueValidator(1)],
        help_text="Requests per minute",
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_check_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def check_status(self):
        """Check provider API status."""
        try:
            client = self.get_client()
            is_healthy = client.check_health()
            
            self.status = "online" if is_healthy else "offline"
            self.last_check_at = timezone.now()
            self.save(update_fields=["status", "last_check_at"])
            
            return is_healthy
            
        except Exception as e:
            self.status = "offline"
            self.last_check_at = timezone.now()
            self.save(update_fields=["status", "last_check_at"])
            return False


class KYCRequest(models.Model):
    """
    Model for tracking KYC verification requests.
    
    Each request can be associated with a financial institution or provider.
    """
    
    REQUEST_TYPES = [
        ("institution", "Financial Institution"),
        ("provider", "Financial Provider"),
    ]
    
    VERIFICATION_TYPES = [
        ("document", "Document Verification"),
        ("face", "Face Verification"),
        ("address", "Address Verification"),
        ("background", "Background Check"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("rejected", "Rejected"),
    ]
    
    request_id = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Request details
    request_type = models.CharField(
        max_length=20,
        choices=REQUEST_TYPES,
    )
    entity_id = models.CharField(
        max_length=100,
        help_text="ID of the requesting institution/provider",
    )
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPES,
    )
    
    # Subject information
    subject_type = models.CharField(
        max_length=20,
        choices=[
            ("individual", "Individual"),
            ("business", "Business"),
        ],
    )
    subject_id = models.CharField(
        max_length=100,
        help_text="ID of the subject being verified",
    )
    
    # KYC provider
    kyc_provider = models.ForeignKey(
        KYCProvider,
        on_delete=models.CASCADE,
        related_name="kyc_requests",
    )
    
    # Request data
    request_data = models.JSONField(
        help_text="Request-specific data",
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    status_details = models.JSONField(
        default=dict,
        help_text="Detailed status information",
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["request_type", "entity_id"]),
            models.Index(fields=["verification_type"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        return f"{self.request_id} - {self.verification_type}"
    
    def update_status(self, new_status: str, details: dict = None):
        """Update the request status."""
        self.status = new_status
        if details:
            self.status_details.update(details)
        if new_status == "completed":
            self.completed_at = timezone.now()
        self.save()


class KYCResult(models.Model):
    """
    Model for storing KYC verification results.
    
    Each result is linked to a specific KYC request and contains the verification outcome.
    """
    
    kyc_request = models.OneToOneField(
        KYCRequest,
        on_delete=models.CASCADE,
        related_name="result",
    )
    
    # Verification results
    is_verified = models.BooleanField(default=False)
    verification_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="Confidence score of the verification",
    )
    
    # Document verification
    document_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of document verified (e.g., passport, ID card)",
    )
    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Document number",
    )
    document_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Document expiry date",
    )
    
    # Face verification
    face_match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Face match confidence score",
    )
    
    # Address verification
    address_verified = models.BooleanField(
        default=False,
        help_text="Whether the address was verified",
    )
    
    # Background check
    background_check_passed = models.BooleanField(
        default=False,
        help_text="Whether the background check passed",
    )
    
    # Additional information
    additional_data = models.JSONField(
        default=dict,
        help_text="Provider-specific verification data",
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_verified"]),
            models.Index(fields=["verification_score"]),
        ]
    
    def __str__(self):
        return f"{self.kyc_request.request_id} - {'Verified' if self.is_verified else 'Not Verified'}"
