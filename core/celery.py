"""
Celery Configuration for Financial Mediator project.

This module configures Celery for asynchronous task processing.
It includes:
- Celery app initialization
- Task autodiscovery
- Beat schedule configuration
- Task routing rules
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Initialize Celery app
app = Celery("financial_mediator")

# Configure Celery using Django settings
# Namespace 'CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix in Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Configure the Celery beat schedule
app.conf.beat_schedule = {
    # Daily cleanup task
    "cleanup-expired-tokens": {
        "task": "api.tasks.cleanup_expired_tokens",
        "schedule": crontab(hour=0, minute=0),  # Run at midnight
    },
    # Hourly provider status check
    "check-provider-status": {
        "task": "providers.tasks.check_provider_status",
        "schedule": crontab(minute=0),  # Run every hour
    },
    # Every 5 minutes transaction sync
    "sync-transactions": {
        "task": "banking.tasks.sync_transactions",
        "schedule": crontab(minute="*/5"),  # Run every 5 minutes
    },
}

# Configure task routing
app.conf.task_routes = {
    # Route provider tasks to dedicated queue
    "providers.*": {"queue": "provider_tasks"},
    # Route banking tasks to dedicated queue
    "banking.*": {"queue": "banking_tasks"},
    # Default queue for other tasks
    "*": {"queue": "default"},
}

# Task error handling
@app.task(bind=True)
def debug_task(self):
    """Task for debugging Celery configuration."""
    print(f"Request: {self.request!r}")

# Configure task error handlers
@app.on_after_configure.connect
def setup_error_handlers(sender, **kwargs):
    """Set up error handlers for Celery tasks."""
    from celery.signals import task_failure

    @task_failure.connect
    def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
        """Handle task failures by logging them."""
        from django.core.cache import cache
        from datetime import datetime

        # Store failure info in cache for monitoring
        cache_key = f"task_failure:{task_id}"
        failure_info = {
            "task_name": sender.name if sender else "Unknown",
            "task_id": task_id,
            "error": str(exception),
            "timestamp": datetime.utcnow().isoformat(),
        }
        cache.set(cache_key, failure_info, timeout=86400)  # Store for 24 hours
