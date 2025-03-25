"""
Celery Tasks for API Module.

This module contains background tasks for API-related operations including:
- Token cleanup
- Request logging
- Cache maintenance
- Monitoring tasks
"""

from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import logging

logger = logging.getLogger(__name__)

@shared_task(
    name="api.tasks.cleanup_expired_tokens",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def cleanup_expired_tokens(self):
    """
    Clean up expired JWT tokens from the database.
    
    This task:
    1. Removes expired tokens from the outstanding token list
    2. Cleans up the token blacklist
    3. Updates token statistics in cache
    
    Returns:
        dict: Summary of cleanup operation
    """
    try:
        # Get current time
        now = timezone.now()
        
        # Remove expired outstanding tokens
        expired_tokens = OutstandingToken.objects.filter(
            expires_at__lt=now
        )
        expired_count = expired_tokens.count()
        expired_tokens.delete()
        
        # Clean up blacklisted tokens
        blacklisted = BlacklistedToken.objects.filter(
            token__expires_at__lt=now
        )
        blacklisted_count = blacklisted.count()
        blacklisted.delete()
        
        # Update statistics in cache
        stats = {
            "last_cleanup": now.isoformat(),
            "expired_tokens_removed": expired_count,
            "blacklisted_tokens_removed": blacklisted_count,
        }
        cache.set("token_cleanup_stats", stats, timeout=86400)  # 24 hours
        
        logger.info(
            "Token cleanup completed",
            extra={
                "expired_count": expired_count,
                "blacklisted_count": blacklisted_count,
            },
        )
        
        return stats
        
    except Exception as e:
        logger.error("Token cleanup failed", exc_info=True)
        raise self.retry(exc=e)

@shared_task(
    name="api.tasks.cleanup_old_requests",
    bind=True,
    max_retries=3,
)
def cleanup_old_requests(self):
    """
    Clean up old request logs from the database.
    
    This task removes request logs older than the configured retention period.
    
    Returns:
        dict: Summary of cleanup operation
    """
    try:
        from api.models import RequestLog
        
        # Calculate cutoff date (30 days ago by default)
        cutoff_date = timezone.now() - timedelta(days=30)
        
        # Delete old requests
        deleted_count = RequestLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]
        
        # Update statistics
        stats = {
            "last_cleanup": timezone.now().isoformat(),
            "deleted_count": deleted_count,
        }
        cache.set("request_cleanup_stats", stats, timeout=86400)
        
        logger.info(
            "Request log cleanup completed",
            extra={"deleted_count": deleted_count},
        )
        
        return stats
        
    except Exception as e:
        logger.error("Request log cleanup failed", exc_info=True)
        raise self.retry(exc=e)

@shared_task(name="api.tasks.update_api_metrics")
def update_api_metrics():
    """
    Update API usage metrics in cache.
    
    This task aggregates various API metrics including:
    - Request counts by endpoint
    - Average response times
    - Error rates
    - Active user count
    
    Returns:
        dict: Updated metrics
    """
    try:
        from api.models import RequestLog
        from django.db.models import Count, Avg
        from django.contrib.auth import get_user_model
        
        # Get the last hour's timestamp
        hour_ago = timezone.now() - timedelta(hours=1)
        
        # Calculate metrics
        metrics = {
            "request_count": RequestLog.objects.filter(
                created_at__gte=hour_ago
            ).count(),
            
            "average_response_time": RequestLog.objects.filter(
                created_at__gte=hour_ago
            ).aggregate(avg_time=Avg("response_time"))["avg_time"],
            
            "error_count": RequestLog.objects.filter(
                created_at__gte=hour_ago,
                response_code__gte=400,
            ).count(),
            
            "active_users": get_user_model().objects.filter(
                last_login__gte=hour_ago
            ).count(),
        }
        
        # Store in cache
        cache.set("api_metrics", metrics, timeout=3600)  # 1 hour
        
        logger.info("API metrics updated", extra=metrics)
        
        return metrics
        
    except Exception as e:
        logger.error("Failed to update API metrics", exc_info=True)
        return None
