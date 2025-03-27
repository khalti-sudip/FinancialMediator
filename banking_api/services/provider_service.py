"""
Provider service module for banking_api.

This service handles all provider-related business logic.
"""

from typing import Optional
from banking_api.models import Provider
from banking_api.exceptions import ProviderError

class ProviderService:
    """Service class for provider operations."""
    
    def register_provider(self, name: str, api_key: str) -> Provider:
        """
        Register a new provider.
        
        Args:
            name: The name of the provider
            api_key: The API key for the provider
            
        Returns:
            The created Provider instance
            
        Raises:
            ProviderError: If the provider registration fails
        """
        try:
            provider = Provider.objects.create(
                name=name,
                api_key=api_key
            )
            return provider
        except Exception as e:
            raise ProviderError(f"Failed to register provider: {str(e)}")
    
    def get_provider(self, provider_id: int) -> Provider:
        """
        Get a provider by ID.
        
        Args:
            provider_id: The ID of the provider to retrieve
            
        Returns:
            The Provider instance
            
        Raises:
            ProviderError: If the provider is not found
        """
        try:
            return Provider.objects.get(pk=provider_id)
        except Provider.DoesNotExist:
            raise ProviderError(f"Provider with ID {provider_id} not found")
    
    def update_provider(self, provider_id: int, **kwargs) -> Provider:
        """
        Update a provider's information.
        
        Args:
            provider_id: The ID of the provider to update
            **kwargs: The fields to update
            
        Returns:
            The updated Provider instance
            
        Raises:
            ProviderError: If the provider is not found or update fails
        """
        try:
            provider = Provider.objects.get(pk=provider_id)
            for key, value in kwargs.items():
                setattr(provider, key, value)
            provider.save()
            return provider
        except Provider.DoesNotExist:
            raise ProviderError(f"Provider with ID {provider_id} not found")
        except Exception as e:
            raise ProviderError(f"Failed to update provider: {str(e)}")
    
    def delete_provider(self, provider_id: int) -> None:
        """
        Delete a provider.
        
        Args:
            provider_id: The ID of the provider to delete
            
        Raises:
            ProviderError: If the provider is not found or deletion fails
        """
        try:
            provider = Provider.objects.get(pk=provider_id)
            provider.delete()
        except Provider.DoesNotExist:
            raise ProviderError(f"Provider with ID {provider_id} not found")
        except Exception as e:
            raise ProviderError(f"Failed to delete provider: {str(e)}")
