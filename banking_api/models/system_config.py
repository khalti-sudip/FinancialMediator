from django.db import models
from django.utils import timezone
from banking_api.models.api_key import ApiKey

class SystemConfig(models.Model):
    """System configuration for providers and integration settings"""
    SYSTEM_TYPE_CHOICES = [
        ('financial_provider', 'Financial Provider'),
        ('banking_system', 'Banking System'),
    ]
    
    AUTH_TYPE_CHOICES = [
        ('api_key', 'API Key'),
        ('oauth', 'OAuth'),
        ('jwt', 'JWT'),
        ('basic', 'Basic Auth'),
    ]
    
    system_name = models.CharField(max_length=100, unique=True, null=False)
    system_type = models.CharField(max_length=50, choices=SYSTEM_TYPE_CHOICES, null=False)
    base_url = models.CharField(max_length=256, null=False)
    auth_type = models.CharField(max_length=50, choices=AUTH_TYPE_CHOICES, default='api_key')
    api_key = models.ForeignKey(
        ApiKey, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='system_configs'
    )
    is_active = models.BooleanField(default=True)
    timeout = models.IntegerField(default=30)  # Request timeout in seconds
    retry_count = models.IntegerField(default=3)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_config'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
        indexes = [
            models.Index(fields=['system_name']),
            models.Index(fields=['system_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f'{self.system_name} - {self.system_type}'
    
    def get_auth_headers(self):
        """Get authentication headers for the system"""
        if not self.api_key:
            return {}
            
        headers = {}
        if self.auth_type == 'api_key':
            headers['X-API-Key'] = self.api_key.key_value
        elif self.auth_type == 'basic':
            # Basic auth would typically be implemented with requests.auth.HTTPBasicAuth
            # But we'll return the values here for reference
            headers['username'] = self.api_key.key_value
            headers['password'] = self.api_key.secret_value
            
        return headers