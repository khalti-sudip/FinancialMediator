"""
Provider Serializers Module.

This module provides serializers for:
- Provider management
- API key handling
- Webhook processing
- Configuration validation
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Provider, ProviderKey, ProviderWebhook

class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for provider data."""
    
    class Meta:
        model = Provider
        fields = [
            "id",
            "name",
            "code",
            "provider_type",
            "supported_currencies",
            "supported_countries",
            "is_active",
            "status",
            "api_base_url",
            "api_version",
            "webhook_url",
            "rate_limit",
            "concurrent_requests",
            "settings",
            "created_at",
            "updated_at",
            "last_check_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_check_at",
        ]
        extra_kwargs = {
            "webhook_secret": {"write_only": True},
            "credentials": {"write_only": True},
        }
    
    def validate_code(self, value):
        """Validate provider code format."""
        # Remove spaces and convert to uppercase
        value = value.strip().upper()
        
        # Check length
        if len(value) < 3 or len(value) > 10:
            raise serializers.ValidationError(
                "Code must be between 3 and 10 characters"
            )
        
        # Check format (alphanumeric)
        if not value.isalnum():
            raise serializers.ValidationError(
                "Code must contain only letters and numbers"
            )
        
        return value
    
    def validate_settings(self, value):
        """Validate provider settings."""
        required_fields = {
            "payment": ["success_url", "cancel_url", "webhook_events"],
            "wallet": ["balance_check_interval", "auto_refund"],
            "bank": ["statement_format", "reconciliation_time"],
            "kyc": ["verification_levels", "required_documents"],
        }
        
        provider_type = self.initial_data.get("provider_type")
        if provider_type:
            for field in required_fields.get(provider_type, []):
                if field not in value:
                    raise serializers.ValidationError(
                        f"Missing required setting for {provider_type}: {field}"
                    )
        
        return value

class ProviderKeySerializer(serializers.ModelSerializer):
    """Serializer for provider API key data."""
    
    class Meta:
        model = ProviderKey
        fields = [
            "id",
            "key_id",
            "provider",
            "is_active",
            "environment",
            "user",
            "daily_limit",
            "monthly_limit",
            "created_at",
            "expires_at",
            "last_used_at",
        ]
        read_only_fields = [
            "id",
            "key_id",
            "created_at",
            "last_used_at",
        ]
        extra_kwargs = {
            "key_data": {"write_only": True},
        }
    
    def validate(self, data):
        """Validate API key data."""
        # Check if key already exists for environment
        if self.instance is None:  # Only for creation
            existing = ProviderKey.objects.filter(
                provider=data["provider"],
                user=data["user"],
                environment=data["environment"],
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    "API key already exists for this environment"
                )
        
        # Validate limits
        if data.get("monthly_limit", 0) < data.get("daily_limit", 0) * 28:
            raise serializers.ValidationError(
                "Monthly limit must be at least 28 times daily limit"
            )
        
        return data

class ProviderWebhookSerializer(serializers.ModelSerializer):
    """Serializer for provider webhook data."""
    
    class Meta:
        model = ProviderWebhook
        fields = [
            "id",
            "event_id",
            "provider",
            "event_type",
            "event_data",
            "status",
            "error_message",
            "retry_count",
            "ip_address",
            "headers",
            "signature",
            "created_at",
            "updated_at",
            "processed_at",
        ]
        read_only_fields = [
            "id",
            "event_id",
            "status",
            "error_message",
            "retry_count",
            "created_at",
            "updated_at",
            "processed_at",
        ]
    
    def validate(self, data):
        """Validate webhook data."""
        # Verify signature
        if not self.instance:  # Only for new webhooks
            provider = data["provider"]
            
            # Skip validation for providers without webhook secret
            if provider.webhook_secret:
                from .utils import calculate_signature
                
                expected = calculate_signature(
                    data["event_data"],
                    provider.webhook_secret,
                )
                
                if data["signature"] != expected:
                    raise serializers.ValidationError(
                        "Invalid webhook signature"
                    )
        
        return data

class ProviderStatusSerializer(serializers.Serializer):
    """Serializer for provider status updates."""
    
    status = serializers.ChoiceField(
        choices=Provider._meta.get_field("status").choices
    )
    message = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)

class ProviderStatsSerializer(serializers.Serializer):
    """Serializer for provider statistics."""
    
    total_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField()
    error_rate = serializers.FloatField()
    active_keys = serializers.IntegerField()
    webhook_success_rate = serializers.FloatField()
    last_update = serializers.DateTimeField()
