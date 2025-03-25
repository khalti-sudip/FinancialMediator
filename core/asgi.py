"""
ASGI Configuration for Financial Mediator project.

This module exposes the ASGI callable as a module-level variable named 'application'.
It allows the application to handle both synchronous HTTP requests and asynchronous
WebSocket connections.

For more information on this file, see:
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Configure the ASGI application
# This will route requests based on their protocol type (HTTP or WebSocket)
application = ProtocolTypeRouter(
    {
        # HTTP requests are handled by Django's ASGI application
        "http": get_asgi_application(),
        
        # WebSocket requests are handled by Channels
        # AuthMiddlewareStack ensures authentication state is available
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)
