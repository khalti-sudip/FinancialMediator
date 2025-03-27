"""
Configuration validator module for FinancialMediator.

This module provides comprehensive validation for all configuration settings in the application.
It uses Pydantic for schema validation and ensures that all required settings are present and valid.

The validator checks:
1. Core settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
2. Database configuration
3. Cache configuration
4. Security settings
5. Authentication settings
6. API rate limiting
7. Provider API keys
8. Logging configuration
9. Monitoring settings
10. Email configuration

Each validation method provides clear error messages to help developers resolve configuration issues.
"""

import os
from typing import Dict, List, Optional, Type
from django.core.exceptions import ImproperlyConfigured
from pydantic import BaseModel, Field, validator, ValidationError
from pydantic.error_wrappers import ErrorWrapper

class ConfigValidator:
    """
    Validator for configuration settings in FinancialMediator.
    
    This class provides methods to validate all configuration settings in the application.
    It uses Pydantic for schema validation and ensures that all required settings are present and valid.
    
    Usage:
    ```python
    try:
        ConfigValidator.validate_all()
    except ImproperlyConfigured as e:
        print(f"Configuration error: {e}")
    ```
    """
    
    class ConfigSchema(BaseModel):
        """
        Configuration schema for FinancialMediator.
        
        This schema defines all configurable settings in the application along with their default values
        and validation rules. Each field has appropriate type hints and validation constraints.
        """
        
        # Core Settings
        DEBUG: bool = Field(
            default=False,
            description="Enable debug mode for development. Should be False in production."
        )
        SECRET_KEY: str = Field(
            min_length=32,
            description="Django secret key used for cryptographic signing. Must be at least 32 characters."
        )
        ALLOWED_HOSTS: List[str] = Field(
            default=['localhost', '127.0.0.1'],
            description="List of allowed hosts for the application."
        )
        
        # Database Settings
        DATABASE_URL: str = Field(
            default='sqlite:///db.sqlite3',
            description="Database connection URL. Supports sqlite, postgresql, and mysql."
        )
        
        # Cache Settings
        CACHE_URL: str = Field(
            default='redis://localhost:6379/1',
            description="Cache connection URL. Supports redis and memcached."
        )
        
        # Security Settings
        SECURE_SSL_REDIRECT: bool = Field(
            default=True,
            description="Enable SSL redirection in production."
        )
        SESSION_COOKIE_SECURE: bool = Field(
            default=True,
            description="Ensure session cookies are only sent over HTTPS."
        )
        CSRF_COOKIE_SECURE: bool = Field(
            default=True,
            description="Ensure CSRF cookies are only sent over HTTPS."
        )
        
        # Authentication Settings
        JWT_SECRET_KEY: str = Field(
            min_length=32,
            description="Secret key for JWT token signing. Must be at least 32 characters."
        )
        JWT_ACCESS_TOKEN_LIFETIME: int = Field(
            default=3600,
            description="Lifetime of JWT access tokens in seconds (default: 1 hour)."
        )
        JWT_REFRESH_TOKEN_LIFETIME: int = Field(
            default=86400,
            description="Lifetime of JWT refresh tokens in seconds (default: 24 hours)."
        )
        
        # API Settings
        API_RATE_LIMIT: int = Field(
            default=100,
            description="Number of requests allowed per minute for API rate limiting."
        )
        API_WINDOW: int = Field(
            default=60,
            description="Time window in seconds for API rate limiting (default: 1 minute)."
        )
        
        # Provider Settings
        PROVIDER_API_KEYS: Dict[str, str] = Field(
            default_factory=dict,
            description="Dictionary of provider API keys. Format: {provider_name: api_key}"
        )
        
        # Logging Settings
        LOG_LEVEL: str = Field(
            default='INFO',
            description="Log level for the application. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
        
        # Monitoring Settings
        OTEL_SERVICE_NAME: str = Field(
            default='financial-mediator',
            description="OpenTelemetry service name for tracing and metrics."
        )
        OTEL_SERVICE_VERSION: str = Field(
            default='1.0.0',
            description="Version of the service being monitored."
        )
        OTEL_DEPLOYMENT_ENVIRONMENT: str = Field(
            default='production',
            description="Deployment environment (production, staging, development)."
        )
        OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = Field(
            default=None,
            description="Optional OTLP endpoint for exporting traces and metrics."
        )
        
        # Email Settings
        EMAIL_HOST: str = Field(
            default='localhost',
            description="SMTP server host for sending emails."
        )
        EMAIL_PORT: int = Field(
            default=587,
            description="SMTP server port."
        )
        EMAIL_USE_TLS: bool = Field(
            default=True,
            description="Enable TLS for email connections."
        )
        EMAIL_HOST_USER: str = Field(
            default='',
            description="SMTP server username for authentication."
        )
        EMAIL_HOST_PASSWORD: str = Field(
            default='',
            description="SMTP server password for authentication."
        )
        
        # Validation methods
        @validator('LOG_LEVEL')
        def validate_log_level(cls, v):
            """
            Validate that the log level is one of the allowed values.
            
            Args:
                v (str): The log level value to validate
                
            Raises:
                ValueError: If the log level is not one of the allowed values
                
            Returns:
                str: The validated log level
            """
            if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                raise ValueError('Invalid log level')
            return v
            
        @validator('DATABASE_URL')
        def validate_database_url(cls, v):
            """
            Validate that the database URL is in a supported format.
            
            Args:
                v (str): The database URL to validate
                
            Raises:
                ValueError: If the database URL is not in a supported format
                
            Returns:
                str: The validated database URL
            """
            if not v.startswith(('sqlite://', 'postgresql://', 'mysql://')):
                raise ValueError('Invalid database URL')
            return v
            
        @validator('CACHE_URL')
        def validate_cache_url(cls, v):
            """
            Validate that the cache URL is in a supported format.
            
            Args:
                v (str): The cache URL to validate
                
            Raises:
                ValueError: If the cache URL is not in a supported format
                
            Returns:
                str: The validated cache URL
            """
            if not v.startswith(('redis://', 'memcached://')):
                raise ValueError('Invalid cache URL')
            return v
            
        @validator('API_RATE_LIMIT')
        def validate_rate_limit(cls, v):
            """
            Validate that the API rate limit is a positive number.
            
            Args:
                v (int): The API rate limit value to validate
                
            Raises:
                ValueError: If the rate limit is not positive
                
            Returns:
                int: The validated rate limit
            """
            if v < 0:
                raise ValueError('Rate limit must be positive')
            return v
            
        @validator('API_WINDOW')
        def validate_window(cls, v):
            """
            Validate that the API window is a positive number.
            
            Args:
                v (int): The API window value to validate
                
            Raises:
                ValueError: If the window is not positive
                
            Returns:
                int: The validated window
            """
            if v < 0:
                raise ValueError('Window must be positive')
            return v
            
        @validator('PROVIDER_API_KEYS')
        def validate_provider_api_keys(cls, v):
            """
            Validate that provider API keys are in the correct format.
            
            Args:
                v (dict): The provider API keys to validate
                
            Raises:
                ValueError: If provider API keys are not in dictionary format
                
            Returns:
                dict: The validated provider API keys
            """
            if not isinstance(v, dict):
                raise ValueError('Provider API keys must be a dictionary')
            return v
            
        @validator('EMAIL_PORT')
        def validate_email_port(cls, v):
            """
            Validate that the email port is within the valid range.
            
            Args:
                v (int): The email port to validate
                
            Raises:
                ValueError: If the email port is not within the valid range
                
            Returns:
                int: The validated email port
            """
            if v < 0 or v > 65535:
                raise ValueError('Invalid email port')
            return v
            
    @staticmethod
    def validate():
        """
        Validate all configuration settings using Pydantic schema.
        
        This method:
        1. Collects all environment variables
        2. Validates them against the ConfigSchema
        3. Raises ImproperlyConfigured with detailed error messages if validation fails
        
        Raises:
            ImproperlyConfigured: If any configuration settings are invalid
        """
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
        """
        Validate that all required settings are present.
        
        This method checks for the presence of critical configuration settings that are required
        for the application to function properly.
        
        Raises:
            ImproperlyConfigured: If any required settings are missing
        """
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
        """
        Validate security-related settings.
        
        This method ensures that all security-critical settings are properly configured.
        
        Raises:
            ImproperlyConfigured: If any security settings are missing or invalid
        """
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
        """
        Validate monitoring-related settings.
        
        This method ensures that all monitoring settings are properly configured for OpenTelemetry.
        
        Raises:
            ImproperlyConfigured: If any monitoring settings are missing
        """
        if not os.environ.get('OTEL_SERVICE_NAME'):
            raise ImproperlyConfigured("OTEL_SERVICE_NAME is required")
            
        if not os.environ.get('OTEL_SERVICE_VERSION'):
            raise ImproperlyConfigured("OTEL_SERVICE_VERSION is required")
            
        if not os.environ.get('OTEL_DEPLOYMENT_ENVIRONMENT'):
            raise ImproperlyConfigured("OTEL_DEPLOYMENT_ENVIRONMENT is required")
            
    @staticmethod
    def validate_all():
        """
        Validate all settings in the application.
        
        This method runs all validation checks in sequence:
        1. Required settings validation
        2. Security settings validation
        3. Monitoring settings validation
        4. Full schema validation
        
        Raises:
            ImproperlyConfigured: If any settings are invalid
        """
        ConfigValidator.validate_required_settings()
        ConfigValidator.validate_security_settings()
        ConfigValidator.validate_monitoring_settings()
        ConfigValidator.validate()

# Run validation when module is imported
ConfigValidator.validate_all()
