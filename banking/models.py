"""
Banking Models Module.

This module defines models for:
- Bank accounts
- Transactions
- Payment methods
- Bank integrations
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class BankAccount(models.Model):
    """Model for storing bank account information."""
    
    # Account identifiers
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=100)
    branch_code = models.CharField(max_length=20)
    
    # Account holder details
    holder_name = models.CharField(max_length=200)
    holder_type = models.CharField(
        max_length=20,
        choices=[
            ("individual", "Individual"),
            ("business", "Business"),
        ],
        default="individual",
    )
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    
    # Account type and currency
    account_type = models.CharField(
        max_length=20,
        choices=[
            ("savings", "Savings"),
            ("checking", "Checking"),
            ("business", "Business"),
        ],
    )
    currency = models.CharField(max_length=3, default="NPR")
    
    # Balance tracking
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account_number"]),
            models.Index(fields=["holder_name"]),
        ]
    
    def __str__(self):
        return f"{self.holder_name} - {self.account_number}"

class Transaction(models.Model):
    """Model for tracking financial transactions."""
    
    # Transaction identifiers
    transaction_id = models.CharField(max_length=100, unique=True)
    reference_id = models.CharField(max_length=100, blank=True)
    
    # Transaction details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="NPR")
    
    # Transaction type and status
    transaction_type = models.CharField(
        max_length=20,
        choices=[
            ("deposit", "Deposit"),
            ("withdrawal", "Withdrawal"),
            ("transfer", "Transfer"),
        ],
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("reversed", "Reversed"),
        ],
        default="pending",
    )
    
    # Account references
    source_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="outgoing_transactions",
    )
    destination_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
        related_name="incoming_transactions",
        null=True,
        blank=True,
    )
    
    # Transaction metadata
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    
    # Error tracking
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_id}"

class PaymentMethod(models.Model):
    """Model for storing payment method information."""
    
    # Method details
    name = models.CharField(max_length=100)
    method_type = models.CharField(
        max_length=20,
        choices=[
            ("card", "Card"),
            ("bank", "Bank Transfer"),
            ("wallet", "Digital Wallet"),
        ],
    )
    
    # Provider information
    provider = models.CharField(max_length=100)
    provider_method_id = models.CharField(max_length=100)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # User association
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_methods",
    )
    
    # Method details (encrypted)
    encrypted_data = models.TextField()
    last_four = models.CharField(max_length=4, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-is_default", "-created_at"]
        unique_together = [["user", "provider", "provider_method_id"]]
    
    def __str__(self):
        return f"{self.name} - {self.last_four}"

class BankIntegration(models.Model):
    """Model for managing bank integrations."""
    
    # Bank details
    bank_name = models.CharField(max_length=100)
    bank_code = models.CharField(max_length=20, unique=True)
    
    # Integration status
    is_active = models.BooleanField(default=True)
    integration_type = models.CharField(
        max_length=20,
        choices=[
            ("api", "API"),
            ("file", "File Transfer"),
            ("manual", "Manual"),
        ],
    )
    
    # Connection details
    api_base_url = models.URLField(blank=True)
    api_version = models.CharField(max_length=10, blank=True)
    
    # Authentication (encrypted)
    auth_credentials = models.TextField()
    
    # Configuration
    settings = models.JSONField(default=dict)
    rate_limits = models.JSONField(default=dict)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["bank_name"]
    
    def __str__(self):
        return f"{self.bank_name} ({self.integration_type})"
