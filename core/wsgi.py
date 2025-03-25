"""
WSGI Configuration for Financial Mediator project.

This module exposes the WSGI callable as a module-level variable named 'application'.
It is used by Django's development server and any WSGI-compatible web server to serve
the Django application.

For more information on this file, see:
https://docs.djangoproject.com/en/stable/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Get the WSGI application
application = get_wsgi_application()

# Wrap the application with WhiteNoise for serving static files
# This is more efficient than letting Django handle static files
application = WhiteNoise(application)
application.add_files("staticfiles", prefix="static/")
