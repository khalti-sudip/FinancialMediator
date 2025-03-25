"""
API Serializers Module.

This module provides serializers for:
- Request/Response data validation
- Model serialization
- Data transformation
- Nested relationship handling
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import RequestLog, APIKey, AuditLog

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""
    
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]

class RequestLogSerializer(serializers.ModelSerializer):
    """Serializer for request log entries."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RequestLog
        fields = [
            "id",
            "path",
            "method",
            "view_name",
            "user",
            "ip_address",
            "user_agent",
            "response_code",
            "response_time",
            "created_at",
        ]
        read_only_fields = fields

class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys."""
    
    user = UserSerializer(read_only=True)
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            "id",
            "key",
            "name",
            "user",
            "is_active",
            "rate_limit",
            "created_at",
            "last_used_at",
            "expires_at",
        ]
        read_only_fields = ["id", "key", "created_at", "last_used_at"]
        
    def validate_rate_limit(self, value):
        """Validate rate limit is within acceptable range."""
        if value < 1:
            raise serializers.ValidationError(
                "Rate limit must be at least 1"
            )
        if value > 1000:
            raise serializers.ValidationError(
                "Rate limit cannot exceed 1000"
            )
        return value

class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            "id",
            "event_type",
            "description",
            "user",
            "ip_address",
            "metadata",
            "created_at",
        ]
        read_only_fields = fields

class HealthCheckSerializer(serializers.Serializer):
    """Serializer for health check response."""
    
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    services = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
