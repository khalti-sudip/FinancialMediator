"""
Local settings for FinancialMediator.
"""

from .base import *

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DATABASE_NAME', 'financialmediator'),
    'USER': os.getenv('DATABASE_USER', 'postgres'),
    'PASSWORD': os.getenv('DATABASE_PASSWORD', 'postgres'),
    'HOST': os.getenv('DATABASE_HOST', 'localhost'),
    'PORT': os.getenv('DATABASE_PORT', '5432'),
})

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
RATE_LIMIT_DURATION = int(os.getenv('RATE_LIMIT_DURATION', '1'))
RATE_LIMIT_BUCKET_SIZE = int(os.getenv('RATE_LIMIT_BUCKET_SIZE', '1000'))

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
