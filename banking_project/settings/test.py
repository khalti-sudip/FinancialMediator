from .base import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test.db',
    }
}

# Disable Redis for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery for testing
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# Use console backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable rate limiting for testing
RATE_LIMITING_ENABLED = False

# Disable security settings for testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Use faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging for testing
LOGGING_CONFIG = None

# Set test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
