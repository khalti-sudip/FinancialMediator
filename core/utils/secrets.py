"""
Secrets management utility for FinancialMediator.

This module provides a secure way to handle sensitive configurations using environment variables
and optionally a secrets management system (like AWS Secrets Manager or HashiCorp Vault).
"""

import os
import json
from typing import Dict, Any, Optional
import logging
from opentelemetry import trace

# Get the global tracer
tracer = trace.get_tracer(__name__)

class SecretsManager:
    """
    Secrets management class that handles sensitive configurations.
    """
    
    def __init__(self):
        """
        Initialize the secrets manager.
        """
        self.logger = logging.getLogger(__name__)
        self.secrets: Dict[str, Any] = {}
        
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value from environment variables.
        
        Args:
            key: Secret key
            default: Default value if secret not found
            
        Returns:
            Secret value or default if not found
        """
        with tracer.start_as_current_span("get_secret") as span:
            span.set_attribute("key", key)
            
            value = os.getenv(key, default)
            if value is None:
                self.logger.warning(f"Secret not found: {key}")
            
            return value
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration from environment variables.
        
        Returns:
            Dictionary containing database configuration
        """
        with tracer.start_as_current_span("get_database_config"):
            return {
                'ENGINE': self.get_secret('DATABASE_ENGINE', 'django.db.backends.postgresql'),
                'NAME': self.get_secret('DATABASE_NAME', 'financialmediator'),
                'USER': self.get_secret('DATABASE_USER', 'postgres'),
                'PASSWORD': self.get_secret('DATABASE_PASSWORD', 'postgres'),
                'HOST': self.get_secret('DATABASE_HOST', 'localhost'),
                'PORT': self.get_secret('DATABASE_PORT', '5432')
            }
    
    def get_jwt_config(self) -> Dict[str, Any]:
        """
        Get JWT configuration from environment variables.
        
        Returns:
            Dictionary containing JWT configuration
        """
        with tracer.start_as_current_span("get_jwt_config"):
            return {
                'SECRET_KEY': self.get_secret('JWT_SECRET_KEY'),
                'ALGORITHM': self.get_secret('JWT_ALGORITHM', 'HS256'),
                'ACCESS_TOKEN_EXPIRE_MINUTES': int(self.get_secret('JWT_EXPIRE_MINUTES', '30'))
            }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """
        Get Redis configuration from environment variables.
        
        Returns:
            Dictionary containing Redis configuration
        """
        with tracer.start_as_current_span("get_redis_config"):
            return {
                'URL': self.get_secret('REDIS_URL', 'redis://localhost:6379/0'),
                'DB': int(self.get_secret('REDIS_DB', '0'))
            }
    
    def get_celery_config(self) -> Dict[str, Any]:
        """
        Get Celery configuration from environment variables.
        
        Returns:
            Dictionary containing Celery configuration
        """
        with tracer.start_as_current_span("get_celery_config"):
            return {
                'BROKER_URL': self.get_secret('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                'RESULT_BACKEND': self.get_secret('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
            }
    
    def validate_secrets(self) -> Dict[str, str]:
        """
        Validate that all required secrets are present.
        
        Returns:
            Dictionary of missing secrets
        """
        with tracer.start_as_current_span("validate_secrets"):
            required_secrets = [
                'SECRET_KEY',
                'DATABASE_PASSWORD',
                'JWT_SECRET_KEY',
                'REDIS_URL',
                'CELERY_BROKER_URL',
                'CELERY_RESULT_BACKEND'
            ]
            
            missing_secrets = {}
            for secret in required_secrets:
                if not self.get_secret(secret):
                    missing_secrets[secret] = f"Required secret '{secret}' not found"
            
            if missing_secrets:
                self.logger.error(f"Missing required secrets: {json.dumps(missing_secrets)}")
            
            return missing_secrets
    
    def load_secrets(self) -> None:
        """
        Load all secrets and validate them.
        """
        with tracer.start_as_current_span("load_secrets"):
            self.secrets = {
                'database': self.get_database_config(),
                'jwt': self.get_jwt_config(),
                'redis': self.get_redis_config(),
                'celery': self.get_celery_config()
            }
            
            missing = self.validate_secrets()
            if missing:
                raise ValueError(f"Missing required secrets: {json.dumps(missing)}")
    
    def get_all_secrets(self) -> Dict[str, Any]:
        """
        Get all loaded secrets.
        
        Returns:
            Dictionary containing all secrets
        """
        with tracer.start_as_current_span("get_all_secrets"):
            return self.secrets

def get_secrets_manager() -> SecretsManager:
    """
    Get a singleton instance of the secrets manager.
    """
    if not hasattr(get_secrets_manager, "instance"):
        get_secrets_manager.instance = SecretsManager()
    return get_secrets_manager.instance

def initialize_secrets() -> None:
    """
    Initialize and load all secrets.
    """
    manager = get_secrets_manager()
    manager.load_secrets()
    
    # Log successful initialization
    logging.info("Secrets initialized successfully")

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret.
    
    Args:
        key: Secret key
        default: Default value if secret not found
        
    Returns:
        Secret value or default if not found
    """
    return get_secrets_manager().get_secret(key, default)

def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration.
    
    Returns:
        Dictionary containing database configuration
    """
    return get_secrets_manager().get_database_config()

def get_jwt_config() -> Dict[str, Any]:
    """
    Get JWT configuration.
    
    Returns:
        Dictionary containing JWT configuration
    """
    return get_secrets_manager().get_jwt_config()

def get_redis_config() -> Dict[str, Any]:
    """
    Get Redis configuration.
    
    Returns:
        Dictionary containing Redis configuration
    """
    return get_secrets_manager().get_redis_config()

def get_celery_config() -> Dict[str, Any]:
    """
    Get Celery configuration.
    
    Returns:
        Dictionary containing Celery configuration
    """
    return get_secrets_manager().get_celery_config()
