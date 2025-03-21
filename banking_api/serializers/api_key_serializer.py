from rest_framework import serializers
from banking_api.models.api_key import ApiKey

class ApiKeySerializer(serializers.ModelSerializer):
    # Secret value should be write-only for security
    secret_value = serializers.CharField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ApiKey
        fields = [
            'id', 'name', 'key_value', 'secret_value', 'provider_type',
            'is_active', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        """Additional validation for API keys"""
        provider_type = data.get('provider_type')
        if provider_type and provider_type not in ['banking', 'payment', 'authentication', 'marketplace', 'other']:
            raise serializers.ValidationError({
                'provider_type': 'Invalid provider type. Must be one of: banking, payment, authentication, marketplace, other.'
            })
        
        # Validate expiry date
        expires_at = data.get('expires_at')
        if expires_at and expires_at < serializers.DateTimeField().to_internal_value(None):
            raise serializers.ValidationError({
                'expires_at': 'Expiry date cannot be in the past.'
            })
        
        return data