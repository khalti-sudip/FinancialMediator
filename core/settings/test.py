from .development import *

# Use SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test.db',
        'TEST': {
            'NAME': BASE_DIR / 'test.db',
        }
    }
}

# Disable Redis for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery for tests
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'memory://'
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable email sending for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Speed up tests by disabling password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Use faster file storage for tests
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

# Disable logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Disable rate limiting for tests
RATELIMIT_ENABLE = False
