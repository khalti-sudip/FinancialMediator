"""
User service module for banking_api.

This service handles all user-related business logic.
"""

from typing import Optional
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from banking_api.models import User
from banking_api.exceptions import UserNotFoundError, InvalidCredentialsError

UserModel = get_user_model()

class UserService:
    """Service class for user-related operations."""
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create a new user.
        
        Args:
            username: The username for the new user
            email: The email address for the new user
            password: The password for the new user
            
        Returns:
            The created User instance
        """
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return user
    
    def get_user(self, user_id: int) -> User:
        """
        Get a user by ID.
        
        Args:
            user_id: The ID of the user to retrieve
            
        Returns:
            The User instance
            
        Raises:
            UserNotFoundError: If the user is not found
        """
        try:
            return UserModel.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            raise UserNotFoundError(f"User with ID {user_id} not found")
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """
        Update a user's information.
        
        Args:
            user_id: The ID of the user to update
            **kwargs: The fields to update
            
        Returns:
            The updated User instance
            
        Raises:
            UserNotFoundError: If the user is not found
        """
        try:
            user = UserModel.objects.get(pk=user_id)
            for key, value in kwargs.items():
                setattr(user, key, value)
            user.save()
            return user
        except ObjectDoesNotExist:
            raise UserNotFoundError(f"User with ID {user_id} not found")
    
    def delete_user(self, user_id: int) -> None:
        """
        Delete a user.
        
        Args:
            user_id: The ID of the user to delete
            
        Raises:
            UserNotFoundError: If the user is not found
        """
        try:
            user = UserModel.objects.get(pk=user_id)
            user.delete()
        except ObjectDoesNotExist:
            raise UserNotFoundError(f"User with ID {user_id} not found")
