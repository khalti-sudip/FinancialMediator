"""
API Models Module.

This module defines the database models for the API application including:
- Request logging
- API keys
- Rate limiting
- Audit trails
"""

from django.db import models
from django.conf import settings
from django.utils import timezone

class RequestLog(models.Model):
    """Model for logging API requests."""
    
    # Request details
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    view_name = models.CharField(max_length=100, null=True, blank=True)
    
    # User information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    # Response information
    response_code = models.IntegerField()
    response_time = models.FloatField(help_text="Response time in seconds")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["user"]),
            models.Index(fields=["path"]),
        ]
        
    def __str__(self):
        return f"{self.method} {self.path} ({self.response_code})"

class APIKey(models.Model):
    """Model for managing API keys."""
    
    # Key details
    key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    
    # Access control
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    is_active = models.BooleanField(default=True)
    
    # Rate limiting
    rate_limit = models.IntegerField(
        default=100,
        help_text="Maximum requests per hour",
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        
    def __str__(self):
        return f"{self.name} ({self.key[:8]}...)"
        
    def is_valid(self):
        """Check if the API key is valid and not expired."""
        if not self.is_active:
            return False
            
        if self.expires_at and timezone.now() >= self.expires_at:
            return False
            
        return True
        
    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

class AuditLog(models.Model):
    """Model for tracking important system events."""
    
    # Event details
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    
    # Actor information
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
        ]
        
    def __str__(self):
        return f"{self.event_type} by {self.user or 'system'}"
