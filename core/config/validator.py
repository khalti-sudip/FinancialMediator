import os
from typing import Dict, List, Optional, Type
from django.core.exceptions import ImproperlyConfigured
from pydantic import BaseModel, Field, validator, ValidationError
from pydantic.error_wrappers import ErrorWrapper

class ConfigValidator:
    """Validator for configuration settings."""
    
    class ConfigSchema(BaseModel):
        """Base configuration schema."""
        
        # Core Settings
        DEBUG: bool = Field(default=False)
        SECRET_KEY: str = Field(min_length=32)
        ALLOWED_HOSTS: List[str] = Field(default=['localhost', '127.0.0.1'])
        
        # Database Settings
        DATABASE_URL: str = Field(default='sqlite:///db.sqlite3')
        
        # Cache Settings
        CACHE_URL: str = Field(default='redis://localhost:6379/1')
        
        # Security Settings
        SECURE_SSL_REDIRECT: bool = Field(default=True)
        SESSION_COOKIE_SECURE: bool = Field(default=True)
        CSRF_COOKIE_SECURE: bool = Field(default=True)
        
        # Authentication Settings
        JWT_SECRET_KEY: str = Field(min_length=32)
        JWT_ACCESS_TOKEN_LIFETIME: int = Field(default=3600)
        JWT_REFRESH_TOKEN_LIFETIME: int = Field(default=86400)
        
        # API Settings
        API_RATE_LIMIT: int = Field(default=100)
        API_WINDOW: int = Field(default=60)
        
        # Provider Settings
        PROVIDER_API_KEYS: Dict[str, str] = Field(default_factory=dict)
        
        # Logging Settings
        LOG_LEVEL: str = Field(default='INFO')
        
        # Monitoring Settings
        OTEL_SERVICE_NAME: str = Field(default='financial-mediator')
        OTEL_SERVICE_VERSION: str = Field(default='1.0.0')
        OTEL_DEPLOYMENT_ENVIRONMENT: str = Field(default='production')
        OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(default=None)
        
        # Email Settings
        EMAIL_HOST: str = Field(default='localhost')
        EMAIL_PORT: int = Field(default=587)
        EMAIL_USE_TLS: bool = Field(default=True)
        EMAIL_HOST_USER: str = Field(default='')
        EMAIL_HOST_PASSWORD: str = Field(default='')
        
        # Validation
        @validator('LOG_LEVEL')
        def validate_log_level(cls, v):
            if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                raise ValueError('Invalid log level')
            return v
            
        @validator('DATABASE_URL')
        def validate_database_url(cls, v):
            if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
                raise ValueError('Invalid database URL')
            return v
            
        @validator('CACHE_URL')
        def validate_cache_url(cls, v):
            if not v.startswith(('redis://', 'memcached://')):
                raise ValueError('Invalid cache URL')
            return v
            
        @validator('API_RATE_LIMIT')
        def validate_rate_limit(cls, v):
            if v < 0:
                raise ValueError('Rate limit must be positive')
            return v
            
        @validator('API_WINDOW')
        def validate_window(cls, v):
            if v < 0:
                raise ValueError('Window must be positive')
            return v
            
        @validator('PROVIDER_API_KEYS')
        def validate_provider_api_keys(cls, v):
            if not isinstance(v, dict):
                raise ValueError('Provider API keys must be a dictionary')
            return v
            
        @validator('EMAIL_PORT')
        def validate_email_port(cls, v):
            if v < 0 or v > 65535:
                raise ValueError('Invalid email port')
            return v
            
    @staticmethod
    def validate():
        """Validate all configuration settings."""
        try:
            # Create environment variables dictionary
            env = {}
            for key in dir(os.environ):
                if key.isupper():
                    env[key] = os.environ[key]
            
            # Validate configuration
            ConfigValidator.ConfigSchema(**env)
            
        except ValidationError as e:
            errors = []
            for error in e.errors():
                loc = '.'.join(str(l) for l in error['loc'])
                errors.append(f"{loc}: {error['msg']}")
            
            raise ImproperlyConfigured(
                "Configuration validation failed:\n" +
                "\n".join(f"- {error}" for error in errors)
            )
            
    @staticmethod
    def validate_required_settings():
        """Validate required settings."""
        required_settings = [
            'SECRET_KEY',
            'DATABASE_URL',
            'JWT_SECRET_KEY',
            'OTEL_SERVICE_NAME',
            'OTEL_SERVICE_VERSION',
            'OTEL_DEPLOYMENT_ENVIRONMENT'
        ]
        
        missing_settings = []
        for setting in required_settings:
            if not os.environ.get(setting):
                missing_settings.append(setting)
        
        if missing_settings:
            raise ImproperlyConfigured(
                "Missing required settings:\n" +
                "\n".join(f"- {setting}" for setting in missing_settings)
            )
            
    @staticmethod
    def validate_security_settings():
        """Validate security-related settings."""
        if not os.environ.get('SECRET_KEY'):
            raise ImproperlyConfigured("SECRET_KEY is required")
            
        if not os.environ.get('JWT_SECRET_KEY'):
            raise ImproperlyConfigured("JWT_SECRET_KEY is required")
            
        if not os.environ.get('DATABASE_URL'):
            raise ImproperlyConfigured("DATABASE_URL is required")
            
        if not os.environ.get('CACHE_URL'):
            raise ImproperlyConfigured("CACHE_URL is required")
            
    @staticmethod
    def validate_monitoring_settings():
        """Validate monitoring-related settings."""
        if not os.environ.get('OTEL_SERVICE_NAME'):
            raise ImproperlyConfigured("OTEL_SERVICE_NAME is required")
            
        if not os.environ.get('OTEL_SERVICE_VERSION'):
            raise ImproperlyConfigured("OTEL_SERVICE_VERSION is required")
            
        if not os.environ.get('OTEL_DEPLOYMENT_ENVIRONMENT'):
            raise ImproperlyConfigured("OTEL_DEPLOYMENT_ENVIRONMENT is required")
            
    @staticmethod
    def validate_all():
        """Validate all settings."""
        ConfigValidator.validate_required_settings()
        ConfigValidator.validate_security_settings()
        ConfigValidator.validate_monitoring_settings()
        ConfigValidator.validate()
        
# Run validation when module is imported
ConfigValidator.validate_all()
