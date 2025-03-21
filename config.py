import os
import datetime


class Config:
    """Base configuration."""
    # Flask configuration
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///banking_middleware.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=30)
    
    # API configurations
    BANKING_API_URL = os.environ.get('BANKING_API_URL', 'http://localhost:8001/api')
    BANKING_API_KEY = os.environ.get('BANKING_API_KEY', '')
    
    # Financial service provider configurations
    FSP_API_URL = os.environ.get('FSP_API_URL', 'http://localhost:8002/api')
    FSP_API_KEY = os.environ.get('FSP_API_KEY', '')
    FSP_API_SECRET = os.environ.get('FSP_API_SECRET', '')
    
    # Cache configuration
    CACHE_TYPE = 'SimpleCache'  # Can be 'redis' in production
    CACHE_DEFAULT_TIMEOUT = 300
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(seconds=5)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(seconds=10)


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    # Set more secure values for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=30)
    CACHE_TYPE = 'RedisCache'


# Create a dictionary of configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
