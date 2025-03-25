"""Signal handlers for the providers app."""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Provider, ProviderKey, ProviderWebhook


@receiver(post_save, sender=Provider)
def invalidate_provider_cache(sender, instance, **kwargs):
    """Invalidate provider-related cache when a provider is saved."""
    cache.delete(f"provider:{instance.id}")
    cache.delete("providers:all")


@receiver(post_delete, sender=Provider)
def cleanup_provider_cache(sender, instance, **kwargs):
    """Clean up provider-related cache when a provider is deleted."""
    cache.delete(f"provider:{instance.id}")
    cache.delete("providers:all")


@receiver(post_save, sender=ProviderKey)
def invalidate_key_cache(sender, instance, **kwargs):
    """Invalidate key-related cache when a key is saved."""
    cache.delete(f"provider:{instance.provider_id}:keys")
    cache.delete(f"provider_key:{instance.key_id}")


@receiver(post_save, sender=ProviderWebhook)
def invalidate_webhook_cache(sender, instance, **kwargs):
    """Invalidate webhook-related cache when a webhook is saved."""
    cache.delete(f"provider:{instance.provider_id}:webhooks")
    cache.delete(f"provider_webhook:{instance.event_id}")
