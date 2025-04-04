"""
Sentry configuration for FinancialMediator.

This module sets up Sentry for error tracking and monitoring.
"""

import os
import logging
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def configure_sentry():
    """
    Configure Sentry for the application.
    
    This function sets up:
    1. Sentry SDK with environment-specific configuration
    2. Integrations for Django, Celery, Redis, SQLAlchemy
    3. Environment-specific settings
    """
    # Get environment variables
    env = os.environ
    
    # Only initialize Sentry if SENTRY_DSN is set
    sentry_dsn = env.get("SENTRY_DSN")
    if not sentry_dsn:
        print("Sentry DSN not configured. Running without Sentry.")
        return
    
    try:
        # Configure Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[
                DjangoIntegration(),
                CeleryIntegration(),
                RedisIntegration(),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR  # Send errors as events
                )
            ],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=env.get("SENTRY_ENVIRONMENT", "development"),
            release=env.get("SENTRY_RELEASE", "unknown"),
            debug=env.get("SENTRY_DEBUG", "false").lower() == "true",
            send_default_pii=True,
            traces_sampler=lambda context: 1.0,
            before_send=lambda event, hint: event,
            server_name=env.get("SENTRY_SERVER_NAME", "unknown")
        )

        # Set tags after initialization
        sentry_sdk.set_tag("service", "financial-mediator")
        sentry_sdk.set_tag("version", env.get("SENTRY_SERVICE_VERSION", "1.0.0"))
        
    except Exception as e:
        print(f"Error initializing Sentry: {str(e)}")
        print("Continuing without Sentry...")
        return

def capture_exception(exception: Exception) -> None:
    """
    Capture an exception in Sentry.
    
    Args:
        exception: The exception to capture
    """
    sentry_sdk.capture_exception(exception)

def capture_message(message: str, level: str = "info") -> None:
    """
    Capture a message in Sentry.
    
    Args:
        message: The message to capture
        level: The log level (info, warning, error, fatal)
    """
    sentry_sdk.capture_message(message, level=level)

def set_user(user_id: str, email: str = None) -> None:
    """
    Set the current user in Sentry context.
    
    Args:
        user_id: The user's ID
        email: The user's email (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email
    })

def set_context(name: str, data: dict) -> None:
    """
    Set additional context in Sentry.
    
    Args:
        name: The context name
        data: The context data
    """
    sentry_sdk.set_context(name, data)

def set_tag(key: str, value: str) -> None:
    """
    Set a tag in Sentry.
    
    Args:
        key: The tag key
        value: The tag value
    """
    sentry_sdk.set_tag(key, value)

def add_breadcrumb(category: str, message: str, level: str = "info") -> None:
    """
    Add a breadcrumb in Sentry.
    
    Args:
        category: The breadcrumb category
        message: The breadcrumb message
        level: The breadcrumb level
    """
    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level
    )
