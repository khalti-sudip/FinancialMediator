"""Celery configuration and task definitions."""

from celery import Celery
from flask import Flask
from typing import Any, Dict, Optional
import os


def create_celery(app: Optional[Flask] = None) -> Celery:
    """Create and configure Celery instance.

    Args:
        app: Optional Flask application instance

    Returns:
        Configured Celery instance
    """
    celery = Celery(
        "financial_mediator",
        broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        include=["api.tasks.transaction_tasks"],
    )

    # Configure Celery
    celery.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_always_eager=os.environ.get("CELERY_ALWAYS_EAGER", False),
        broker_connection_retry_on_startup=True,
        task_routes={
            "api.tasks.transaction_tasks.*": {"queue": "transactions"},
            "api.tasks.notification_tasks.*": {"queue": "notifications"},
        },
        task_default_queue="default",
        task_queues={"default": {}, "transactions": {}, "notifications": {}},
    )

    if app:
        # Initialize Celery with Flask context
        class ContextTask(celery.Task):
            def __call__(self, *args: Any, **kwargs: Any) -> Any:
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# Create the Celery instance
celery = create_celery()
