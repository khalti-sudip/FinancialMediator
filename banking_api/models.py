"""
Banking API models for FinancialMediator.

This module defines the core data models for the banking system, including:
1. User accounts and authentication
2. API key management
3. Transaction processing
4. System configuration
5. Audit logging

Each model includes:
- Field definitions with validation
- Relationship definitions
- Custom methods for business logic
- Indexes for performance optimization
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MinValueValidator
import uuid

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Adds additional fields for banking system:
    - UUID for unique identification
    - Account balance
    - Transaction limits
    - KYC status
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    daily_transaction_limit = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=10000,
        validators=[MinValueValidator(0)]
    )
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    
    class Meta:
        """Model metadata."""
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['kyc_status'])
        ]
    
    def has_sufficient_balance(self, amount: float) -> bool:
        """
        Check if user has sufficient balance for a transaction.
        
        Args:
            amount: Transaction amount
            
        Returns:
            bool: True if sufficient balance, False otherwise
        """
        return self.balance >= amount
    
    def can_perform_transaction(self, amount: float) -> bool:
        """
        Check if user can perform a transaction based on limits.
        
        Args:
            amount: Transaction amount
            
        Returns:
            bool: True if transaction is allowed, False otherwise
        """
        return (self.balance >= amount and
                amount <= self.daily_transaction_limit)

class ApiKey(models.Model):
    """
    API key model for system authentication.
    
    Stores API keys with associated permissions and usage tracking.
    
    Key Features:
    - Unique API key generation
    - Expiration management
    - Rate limiting
    - Usage tracking
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    rate_limit = models.IntegerField(default=1000)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        """Model metadata."""
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_active'])
        ]
    
    def is_valid(self) -> bool:
        """
        Check if API key is valid.
        
        Returns:
            bool: True if key is valid, False otherwise
        """
        return (self.is_active and
                (self.expires_at is None or self.expires_at > timezone.now()))
    
    def increment_usage(self) -> None:
        """
        Increment API key usage count and update last used timestamp.
        """
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save(update_fields=['usage_count', 'last_used'])

class Transaction(models.Model):
    """
    Transaction model for tracking financial transactions.
    
    Stores transaction details including:
    - Transaction metadata
    - Amount and currency
    - Status tracking
    - Request/response data
    """
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
        ('refund', 'Refund')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=100, unique=True)
    source_system = models.CharField(max_length=100)
    target_system = models.CharField(max_length=100)
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_data = models.JSONField()
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Model metadata."""
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user_id'])
        ]
    
    def update_status(self, new_status: str, response_data: dict = None) -> None:
        """
        Update transaction status and response data.
        
        Args:
            new_status: New transaction status
            response_data: Response data from external system
        """
        self.status = new_status
        if response_data:
            self.response_data = response_data
        self.save(update_fields=['status', 'response_data', 'updated_at'])

class SystemConfig(models.Model):
    """
    System configuration model for storing application settings.
    
    Stores key-value pairs for:
    - API endpoints
    - Rate limits
    - Thresholds
    - Feature flags
    """
    
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        """Model metadata."""
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['is_active'])
        ]
    
    def deactivate(self) -> None:
        """
        Deactivate the configuration setting.
        """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

class AuditLog(models.Model):
    """
    Audit log model for tracking system events.
    
    Stores detailed logs of:
    - User actions
    - System changes
    - Security events
    - Error occurrences
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    action = models.CharField(max_length=100)
    description = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Model metadata."""
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['action'])
        ]
    
    def log_action(self, action: str, description: str, metadata: dict = None) -> None:
        """
        Log a system action with optional metadata.
        
        Args:
            action: Action type
            description: Action description
            metadata: Additional action metadata
        """
        self.action = action
        self.description = description
        self.metadata = metadata
        self.save()
