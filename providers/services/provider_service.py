"""Service layer for provider management."""

from typing import Optional, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Provider, ProviderKey, ProviderWebhook
from .utils.provider_utils import (
    validate_provider_data,
    generate_provider_key,
    validate_provider_key,
    validate_webhook_url,
    format_webhook_response,
    process_webhook_event,
    get_provider_status,
    log_provider_action,
    get_provider_statistics
)
from banking_api.exceptions import ProviderError
from banking_api.utils.common import format_timestamp

class ProviderService:
    """
    Service class for managing providers.
    
    Handles all business logic related to providers, including creation,
    updates, and validation.
    """
    
    def create_provider(self, data: Dict[str, Any]) -> Provider:
        """
        Create a new provider.
        
        Args:
            data: Dictionary containing provider data
            
        Returns:
            The created Provider instance
            
        Raises:
            ProviderError: If validation fails
        """
        try:
            # Validate data
            validated_data = validate_provider_data(data)
            
            with transaction.atomic():
                provider = Provider.objects.create(**validated_data)
                
                # Log provider creation
                log_provider_action(
                    provider.id,
                    "create",
                    {"name": provider.name, "type": provider.type},
                    self.request
                )
                
                return provider
        except ValidationError as e:
            raise ProviderError(str(e))

    def update_provider(self, provider_id: int, data: Dict[str, Any]) -> Provider:
        """
        Update an existing provider.
        
        Args:
            provider_id: ID of the provider to update
            data: Dictionary containing updated data
            
        Returns:
            The updated Provider instance
            
        Raises:
            ProviderError: If provider not found or validation fails
        """
        try:
            # Validate data
            validated_data = validate_provider_data(data)
            
            provider = Provider.objects.get(id=provider_id)
            for key, value in validated_data.items():
                setattr(provider, key, value)
            provider.save()
            
            # Log provider update
            log_provider_action(
                provider.id,
                "update",
                {"updated_fields": list(validated_data.keys())},
                self.request
            )
            
            return provider
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")
        except ValidationError as e:
            raise ProviderError(str(e))

    def delete_provider(self, provider_id: int) -> None:
        """
        Delete a provider.
        
        Args:
            provider_id: ID of the provider to delete
            
        Raises:
            ProviderError: If provider not found
        """
        try:
            provider = Provider.objects.get(id=provider_id)
            
            # Log provider deletion
            log_provider_action(
                provider.id,
                "delete",
                {"name": provider.name},
                self.request
            )
            
            provider.delete()
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")

    def get_provider_status(self, provider_id: int) -> Dict[str, Any]:
        """
        Get the current status of a provider.
        
        Args:
            provider_id: ID of the provider
            
        Returns:
            Dictionary containing provider status information
            
        Raises:
            ProviderError: If provider not found
        """
        return get_provider_status(provider_id)

    def get_provider(self, provider_id: int) -> Provider:
        """
        Get a provider by ID.
        
        Args:
            provider_id: ID of the provider to retrieve
            
        Returns:
            The Provider instance
            
        Raises:
            ProviderError: If provider not found
        """
        try:
            return Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")

    def get_provider_by_name(self, name: str) -> Provider:
        """
        Get a provider by name.
        
        Args:
            name: Name of the provider to retrieve
            
        Returns:
            The Provider instance
            
        Raises:
            ProviderError: If provider not found
        """
        try:
            return Provider.objects.get(name=name)
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")

    def get_all_providers(self) -> list[Provider]:
        """
        Get all providers.
        
        Returns:
            List of Provider instances
        """
        return Provider.objects.all()

class ProviderKeyService:
    """
    Service class for managing provider keys.
    
    Handles all business logic related to provider keys, including creation,
    updates, and validation.
    """
    
    def create_provider_key(self, provider_id: int, data: Dict[str, Any]) -> ProviderKey:
        """
        Create a new provider key.
        
        Args:
            provider_id: ID of the associated provider
            data: Dictionary containing key data
            
        Returns:
            The created ProviderKey instance
            
        Raises:
            ProviderError: If validation fails or provider not found
        """
        try:
            with transaction.atomic():
                provider = Provider.objects.get(id=provider_id)
                
                # Generate key if not provided
                if "key_value" not in data:
                    data["key_value"] = generate_provider_key(provider_id, data.get("key_type", "api"))
                
                # Validate key format
                if not validate_provider_key(data["key_value"]):
                    raise ProviderError("Invalid key format", code="INVALID_KEY")
                
                key = ProviderKey.objects.create(provider=provider, **data)
                
                # Log key creation
                log_provider_action(
                    provider_id,
                    "key_create",
                    {"key_type": data.get("key_type", "api")},
                    self.request
                )
                
                return key
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")
        except ValidationError as e:
            raise ProviderError(str(e))

    def update_provider_key(self, key_id: int, data: Dict[str, Any]) -> ProviderKey:
        """
        Update an existing provider key.
        
        Args:
            key_id: ID of the key to update
            data: Dictionary containing updated data
            
        Returns:
            The updated ProviderKey instance
            
        Raises:
            ProviderError: If key not found or validation fails
        """
        try:
            key = ProviderKey.objects.get(id=key_id)
            
            # Validate key format if updating key_value
            if "key_value" in data and not validate_provider_key(data["key_value"]):
                raise ProviderError("Invalid key format", code="INVALID_KEY")
            
            for field, value in data.items():
                setattr(key, field, value)
            key.save()
            
            # Log key update
            log_provider_action(
                key.provider_id,
                "key_update",
                {"updated_fields": list(data.keys())},
                self.request
            )
            
            return key
        except ProviderKey.DoesNotExist:
            raise ProviderError("Provider key not found", code="NOT_FOUND")
        except ValidationError as e:
            raise ProviderError(str(e))

    def delete_provider_key(self, key_id: int) -> None:
        """
        Delete a provider key.
        
        Args:
            key_id: ID of the key to delete
            
        Raises:
            ProviderError: If key not found
        """
        try:
            key = ProviderKey.objects.get(id=key_id)
            
            # Log key deletion
            log_provider_action(
                key.provider_id,
                "key_delete",
                {"key_id": key.id},
                self.request
            )
            
            key.delete()
        except ProviderKey.DoesNotExist:
            raise ProviderError("Provider key not found", code="NOT_FOUND")

    def get_provider_key(self, key_id: int) -> ProviderKey:
        """
        Get a provider key by ID.
        
        Args:
            key_id: ID of the key to retrieve
            
        Returns:
            The ProviderKey instance
            
        Raises:
            ProviderError: If key not found
        """
        try:
            return ProviderKey.objects.get(id=key_id)
        except ProviderKey.DoesNotExist:
            raise ProviderError("Provider key not found", code="NOT_FOUND")

class ProviderWebhookService:
    """
    Service class for managing provider webhooks.
    
    Handles all business logic related to provider webhooks, including creation,
    updates, and validation.
    """
    
    def create_webhook(self, provider_id: int, data: Dict[str, Any]) -> ProviderWebhook:
        """
        Create a new webhook for a provider.
        
        Args:
            provider_id: ID of the associated provider
            data: Dictionary containing webhook data
            
        Returns:
            The created ProviderWebhook instance
            
        Raises:
            ProviderError: If validation fails or provider not found
        """
        try:
            with transaction.atomic():
                provider = Provider.objects.get(id=provider_id)
                
                # Validate webhook URL
                if not validate_webhook_url(data.get("url", "")):
                    raise ProviderError("Invalid webhook URL", code="INVALID_URL")
                
                webhook = ProviderWebhook.objects.create(provider=provider, **data)
                
                # Log webhook creation
                log_provider_action(
                    provider_id,
                    "webhook_create",
                    {"url": data["url"]},
                    self.request
                )
                
                return webhook
        except Provider.DoesNotExist:
            raise ProviderError("Provider not found", code="NOT_FOUND")
        except ValidationError as e:
            raise ProviderError(str(e))

    def process_webhook_event(self, webhook_id: int, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a webhook event.
        
        Args:
            webhook_id: ID of the webhook configuration
            event_type: Type of event being processed
            payload: Event payload data
            
        Returns:
            Processed response dictionary
            
        Raises:
            ProviderError: If webhook processing fails
        """
        return process_webhook_event(webhook_id, event_type, payload)

    def get_webhook(self, webhook_id: int) -> ProviderWebhook:
        """
        Get a webhook by ID.
        
        Args:
            webhook_id: ID of the webhook to retrieve
            
        Returns:
            The ProviderWebhook instance
            
        Raises:
            ProviderError: If webhook not found
        """
        try:
            return ProviderWebhook.objects.get(id=webhook_id)
        except ProviderWebhook.DoesNotExist:
            raise ProviderError("Webhook not found", code="NOT_FOUND")

    def get_webhook_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about webhooks.
        
        Returns:
            Dictionary containing webhook statistics
        """
        stats = {
            "total_webhooks": ProviderWebhook.objects.count(),
            "active_webhooks": ProviderWebhook.objects.filter(is_active=True).count(),
            "provider_webhook_count": {}
        }
        
        # Get webhook count per provider
        for provider in Provider.objects.all():
            stats["provider_webhook_count"][provider.name] = provider.providerwebhook_set.count()
        
        return stats
