"""
Django settings for Financial Mediator project.

This module contains the core settings for the Django application.
It includes configurations for:
- Database connections
- Security settings
- Application configurations
- Third-party integrations
- Logging and monitoring
"""

import os
from pathlib import Path
import environ

# ------------------------
# Environment Configuration
# ------------------------

# Initialize environment variables handler
env = environ.Env(
    # Set default values for critical configurations
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    CORS_ALLOWED_ORIGINS=(list, ['http://localhost:3000']),
)

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ----------------------
# Core Django Settings
# ----------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='your-secret-key-for-development')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# -----------------
# Application Setup
# -----------------

# Base Django apps
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Third-party apps
THIRD_PARTY_APPS = [
    'rest_framework',               # REST API framework
    'rest_framework_simplejwt',     # JWT authentication
    'corsheaders',                 # Cross-Origin Resource Sharing
    'django_filters',              # Advanced filtering
    'drf_spectacular',            # API documentation
    'django_prometheus',          # Metrics and monitoring
    'django_celery_beat',        # Periodic tasks
    'django_celery_results',     # Store task results
]

# Local project apps
LOCAL_APPS = [
    'api.apps.ApiConfig',
    'providers.apps.ProvidersConfig',
    'banking.apps.BankingConfig',
]

# Combine all apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ----------------------
# Middleware Configuration
# ----------------------

MIDDLEWARE = [
    # Monitoring - should be first to accurately measure request timing
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    
    # Security and CORS
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    
    # Static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # Django default middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom middleware
    'api.middleware.request_tracking.RequestTrackingMiddleware',
    
    # Monitoring - should be last to accurately measure response timing
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# -------------------
# URL Configuration
# -------------------

ROOT_URLCONF = 'core.urls'

# --------------------
# Template Configuration
# --------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ----------------------
# Database Configuration
# ----------------------

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

# ----------------------
# Cache Configuration
# ----------------------

CACHES = {
    'default': env.cache('REDIS_URL', default='redis://127.0.0.1:6379/1')
}

# ----------------------
# Celery Configuration
# ----------------------

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'default'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes

# ------------------------
# Password Validation Rules
# ------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------
# Internationalization Config
# --------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------
# Static Files Config
# ----------------------

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Set the default primary key field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------
# REST Framework Settings
# ------------------------

REST_FRAMEWORK = {
    # Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
    # Permissions
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    
    # Schema generation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# -------------------
# JWT Settings
# -------------------

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ACCESS_TOKEN_LIFETIME': env('JWT_ACCESS_TOKEN_LIFETIME', default=60 * 60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': env('JWT_REFRESH_TOKEN_LIFETIME', default=24 * 60 * 60),  # 1 day
}

# -------------------
# CORS Settings
# -------------------

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_CREDENTIALS = True

# ------------------------
# API Documentation Settings
# ------------------------

SPECTACULAR_SETTINGS = {
    'TITLE': 'Financial Mediator API',
    'DESCRIPTION': 'API for financial transaction mediation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# -------------------
# Prometheus Settings
# -------------------

PROMETHEUS_EXPORT_MIGRATIONS = False

# -------------------
# Sentry Integration
# -------------------

if not DEBUG and env('SENTRY_DSN', default=None):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=env('SENTRY_DSN'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.1),
    )

# -------------------
# Logging Configuration
# -------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Define log formatters
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    
    # Configure log handlers
    'handlers': {
        # Console output
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        # File output with rotation
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'financial_mediator.log',
            'maxBytes': 10 * 1024 * 1024,  # 10 MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    
    # Root logger configuration
    'root': {
        'handlers': ['console', 'file'],
        'level': env('LOG_LEVEL', default='INFO'),
    },
    
    # App-specific loggers
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
