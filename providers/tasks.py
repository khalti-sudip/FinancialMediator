"""
Provider Tasks Module.

This module provides Celery tasks for:
- Provider status monitoring
- API key management
- Webhook processing
- Statistics collection
"""

from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Avg, Count
from django.conf import settings
import logging

from .models import Provider, ProviderKey, ProviderWebhook

logger = logging.getLogger(__name__)

@shared_task(
    name="providers.tasks.check_provider_status",
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 minutes
)
def check_provider_status(self):
    """
    Check status of all active providers.
    
    This task:
    1. Checks API connectivity
    2. Updates provider status
    3. Sends notifications if needed
    
    Returns:
        dict: Status check results
    """
    try:
        # Get active providers
        providers = Provider.objects.filter(is_active=True)
        
        results = {
            "total": providers.count(),
            "online": 0,
            "offline": 0,
            "errors": [],
        }
        
        # Check each provider
        for provider in providers:
            try:
                # Check status
                is_healthy = provider.check_status()
                
                # Update counters
                if is_healthy:
                    results["online"] += 1
                else:
                    results["offline"] += 1
                    
                    # Send notification if newly offline
                    if provider.status != "offline":
                        notify_provider_status.delay(
                            provider.id,
                            "offline"
                        )
                
            except Exception as e:
                logger.error(
                    f"Failed to check {provider.name}",
                    exc_info=True
                )
                results["errors"].append({
                    "provider": provider.code,
                    "error": str(e),
                })
        
        # Cache results
        cache.set(
            "provider_status",
            results,
            timeout=settings.STATUS_CHECK_CACHE_TTL
        )
        
        return results
        
    except Exception as e:
        logger.error("Provider status check failed", exc_info=True)
        raise self.retry(exc=e)

@shared_task(
    name="providers.tasks.process_webhook",
    bind=True,
    max_retries=3,
)
def process_webhook(self, webhook_id):
    """
    Process a provider webhook event.
    
    Args:
        webhook_id: ID of webhook to process
        
    Returns:
        bool: True if processed successfully
    """
    try:
        # Get webhook
        webhook = ProviderWebhook.objects.get(id=webhook_id)
        
        # Skip if already processed
        if webhook.status in ["completed", "failed"]:
            return True
        
        # Update status
        webhook.status = "processing"
        webhook.save(update_fields=["status"])
        
        try:
            # Get handler
            handler = get_webhook_handler(
                webhook.provider.provider_type,
                webhook.event_type,
            )
            
            # Process event
            handler(webhook.event_data)
            
            # Mark as completed
            webhook.status = "completed"
            webhook.processed_at = timezone.now()
            webhook.save(update_fields=["status", "processed_at"])
            
            return True
            
        except Exception as e:
            # Handle failure
            webhook.status = "failed"
            webhook.error_message = str(e)
            webhook.retry_count += 1
            webhook.save()
            
            # Retry if attempts remain
            if webhook.retry_count < settings.WEBHOOK_MAX_RETRIES:
                raise self.retry(exc=e)
            
            return False
        
    except Exception as e:
        logger.error(f"Failed to process webhook {webhook_id}", exc_info=True)
        return False

@shared_task(name="providers.tasks.cleanup_expired_keys")
def cleanup_expired_keys():
    """
    Clean up expired API keys.
    
    This task:
    1. Deactivates expired keys
    2. Removes old key data
    3. Updates statistics
    
    Returns:
        dict: Cleanup results
    """
    try:
        # Get expired keys
        expired_keys = ProviderKey.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now(),
        )
        
        results = {
            "deactivated": 0,
            "errors": [],
        }
        
        # Process each key
        for key in expired_keys:
            try:
                # Deactivate key
                key.is_active = False
                key.save(update_fields=["is_active"])
                
                results["deactivated"] += 1
                
            except Exception as e:
                logger.error(
                    f"Failed to deactivate key {key.key_id}",
                    exc_info=True
                )
                results["errors"].append({
                    "key": str(key.key_id),
                    "error": str(e),
                })
        
        return results
        
    except Exception as e:
        logger.error("Key cleanup failed", exc_info=True)
        return None

@shared_task(name="providers.tasks.collect_provider_stats")
def collect_provider_stats():
    """
    Collect provider usage statistics.
    
    This task:
    1. Calculates request rates
    2. Measures response times
    3. Tracks error rates
    4. Updates provider metrics
    
    Returns:
        dict: Provider statistics
    """
    try:
        # Calculate time range
        end_time = timezone.now()
        start_time = end_time - timezone.timedelta(hours=1)
        
        # Get active providers
        providers = Provider.objects.filter(is_active=True)
        
        stats = {}
        
        # Collect stats for each provider
        for provider in providers:
            # Get webhooks
            webhooks = ProviderWebhook.objects.filter(
                provider=provider,
                created_at__range=[start_time, end_time],
            )
            
            # Calculate metrics
            total_webhooks = webhooks.count()
            successful_webhooks = webhooks.filter(
                status="completed"
            ).count()
            
            # Store stats
            stats[provider.code] = {
                "total_requests": total_webhooks,
                "success_rate": (
                    successful_webhooks / total_webhooks
                    if total_webhooks > 0 else 0
                ),
                "average_response_time": webhooks.aggregate(
                    avg_time=Avg("response_time")
                )["avg_time"] or 0,
                "error_rate": webhooks.filter(
                    status="failed"
                ).count() / total_webhooks if total_webhooks > 0 else 0,
                "active_keys": ProviderKey.objects.filter(
                    provider=provider,
                    is_active=True,
                ).count(),
            }
        
        # Cache results
        cache.set(
            "provider_stats",
            stats,
            timeout=settings.STATS_CACHE_TTL
        )
        
        return stats
        
    except Exception as e:
        logger.error("Failed to collect provider stats", exc_info=True)
        return None

@shared_task
def notify_provider_status(provider_id, status):
    """
    Send notification about provider status change.
    
    Args:
        provider_id: ID of the provider
        status: New status
    """
    try:
        # Get provider
        provider = Provider.objects.get(id=provider_id)
        
        # Get notification service
        notification_service = get_notification_service()
        
        # Send notification
        notification_service.send_alert(
            title=f"Provider Status Change: {provider.name}",
            message=f"Provider {provider.name} is now {status}",
            severity="high" if status == "offline" else "info",
            metadata={
                "provider": provider.code,
                "status": status,
                "timestamp": timezone.now().isoformat(),
            },
        )
        
    except Exception as e:
        logger.error(
            f"Failed to notify about provider {provider_id}",
            exc_info=True
        )
