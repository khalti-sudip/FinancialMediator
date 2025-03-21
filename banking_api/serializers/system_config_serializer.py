from rest_framework import serializers
from banking_api.models.system_config import SystemConfig
from banking_api.serializers.api_key_serializer import ApiKeySerializer

class SystemConfigSerializer(serializers.ModelSerializer):
    # Add a nested serializer for api_key
    api_key = ApiKeySerializer(required=False, read_only=True)
    api_key_id = serializers.PrimaryKeyRelatedField(
        source='api_key',
        queryset=SystemConfig.api_key.field.related_model.objects.all(),
        required=False,
        write_only=True,
        allow_null=True
    )
    
    class Meta:
        model = SystemConfig
        fields = [
            'id', 'system_name', 'system_type', 'base_url', 'auth_type',
            'api_key', 'api_key_id', 'is_active', 'timeout', 'retry_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Additional validation for system configurations"""
        auth_type = data.get('auth_type')
        api_key = data.get('api_key')
        
        # If auth_type is api_key, an API key should be provided
        if auth_type == 'api_key' and not api_key and not self.instance.api_key:
            raise serializers.ValidationError({
                'api_key_id': 'An API key must be provided when auth_type is set to "api_key".'
            })
        
        # Validate base_url format
        base_url = data.get('base_url')
        if base_url and not (base_url.startswith('http://') or base_url.startswith('https://')):
            raise serializers.ValidationError({
                'base_url': 'Base URL must start with "http://" or "https://".'
            })
        
        return data