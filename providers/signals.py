"""Signal handlers for the providers app."""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Provider, ProviderEndpoint, ProviderCredential


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


@receiver(post_save, sender=ProviderEndpoint)
def invalidate_endpoint_cache(sender, instance, **kwargs):
    """Invalidate endpoint-related cache when an endpoint is saved."""
    cache.delete(f"provider:{instance.provider_id}:endpoints")


@receiver(post_save, sender=ProviderCredential)
def invalidate_credential_cache(sender, instance, **kwargs):
    """Invalidate credential-related cache when a credential is saved."""
    cache.delete(f"provider:{instance.provider_id}:credentials")
