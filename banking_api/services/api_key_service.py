"""
API Key service module for banking_api.

This service handles all API key-related business logic.
"""

from typing import Optional
from django.db import transaction
from banking_api.models import APIKey
from banking_api.exceptions import APIKeyError

class APIKeyService:
    """Service class for API key operations."""
    
    def generate_api_key(self, user_id: int, name: str) -> APIKey:
        """
        Generate a new API key for a user.
        
        Args:
            user_id: The ID of the user
            name: The name for the API key
            
        Returns:
            The created APIKey instance
            
        Raises:
            APIKeyError: If API key generation fails
        """
        try:
            with transaction.atomic():
                api_key = APIKey.objects.create(
                    user_id=user_id,
                    name=name
                )
                return api_key
        except Exception as e:
            raise APIKeyError(f"Failed to generate API key: {str(e)}")
    
    def get_api_key(self, key_id: int) -> APIKey:
        """
        Get an API key by ID.
        
        Args:
            key_id: The ID of the API key to retrieve
            
        Returns:
            The APIKey instance
            
        Raises:
            APIKeyError: If the API key is not found
        """
        try:
            return APIKey.objects.get(pk=key_id)
        except APIKey.DoesNotExist:
            raise APIKeyError(f"API key with ID {key_id} not found")
    
    def get_api_key_by_value(self, value: str) -> APIKey:
        """
        Get an API key by its value.
        
        Args:
            value: The API key value
            
        Returns:
            The APIKey instance
            
        Raises:
            APIKeyError: If the API key is not found
        """
        try:
            return APIKey.objects.get(value=value)
        except APIKey.DoesNotExist:
            raise APIKeyError(f"API key {value} not found")
    
    def update_api_key(self, key_id: int, **kwargs) -> APIKey:
        """
        Update an API key's information.
        
        Args:
            key_id: The ID of the API key to update
            **kwargs: The fields to update
            
        Returns:
            The updated APIKey instance
            
        Raises:
            APIKeyError: If the API key is not found or update fails
        """
        try:
            api_key = APIKey.objects.get(pk=key_id)
            for key, value in kwargs.items():
                setattr(api_key, key, value)
            api_key.save()
            return api_key
        except APIKey.DoesNotExist:
            raise APIKeyError(f"API key with ID {key_id} not found")
        except Exception as e:
            raise APIKeyError(f"Failed to update API key: {str(e)}")
    
    def delete_api_key(self, key_id: int) -> None:
        """
        Delete an API key.
        
        Args:
            key_id: The ID of the API key to delete
            
        Raises:
            APIKeyError: If the API key is not found or deletion fails
        """
        try:
            api_key = APIKey.objects.get(pk=key_id)
            api_key.delete()
        except APIKey.DoesNotExist:
            raise APIKeyError(f"API key with ID {key_id} not found")
        except Exception as e:
            raise APIKeyError(f"Failed to delete API key: {str(e)}")
    
    def validate_api_key(self, value: str) -> bool:
        """
        Validate an API key.
        
        Args:
            value: The API key value to validate
            
        Returns:
            True if the API key is valid, False otherwise
        """
        try:
            api_key = self.get_api_key_by_value(value)
            return api_key.is_active and not api_key.expired
        except APIKeyError:
            return False
