"""
Development server settings for FinancialMediator.
"""

from .base import *

# Debug settings
DEBUG = False
ALLOWED_HOSTS = ['dev.financialmediator.com']

# Database
DATABASES['default'].update({
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.getenv('DATABASE_NAME', 'financialmediator_dev'),
    'USER': os.getenv('DATABASE_USER', 'postgres'),
    'PASSWORD': os.getenv('DATABASE_PASSWORD'),
    'HOST': os.getenv('DATABASE_HOST', 'db-dev'),
    'PORT': os.getenv('DATABASE_PORT', '5432'),
})

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis-dev:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis-dev:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis-dev:6379/1')

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', '500'))
RATE_LIMIT_DURATION = int(os.getenv('RATE_LIMIT_DURATION', '1'))
RATE_LIMIT_BUCKET_SIZE = int(os.getenv('RATE_LIMIT_BUCKET_SIZE', '5000'))

# CORS
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'https://dev.financialmediator.com').split(',')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/financialmediator/dev.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/financialmediator/static'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/financialmediator/media'
