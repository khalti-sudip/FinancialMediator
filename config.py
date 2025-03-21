import os
from datetime import timedelta


class Config:
    """Base configuration"""
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis cache configuration (optional)
    REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Banking API configuration
    BANKING_API_URL = os.environ.get('BANKING_API_URL', 'https://mock-banking-api.example.com')
    BANKING_API_KEY = os.environ.get('BANKING_API_KEY', 'sample-banking-api-key')
    
    # Financial provider default configuration
    DEFAULT_PROVIDER_URL = os.environ.get('DEFAULT_PROVIDER_URL', 'https://mock-provider-api.example.com')
    DEFAULT_PROVIDER_KEY = os.environ.get('DEFAULT_PROVIDER_KEY', 'sample-provider-api-key')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    
    # Transaction configuration
    TRANSACTION_TIMEOUT = int(os.environ.get('TRANSACTION_TIMEOUT', '3600'))  # 1 hour in seconds
