"""
Tests for the user service.
"""

import pytest
from django.contrib.auth import get_user_model
from banking_api.services.user_service import UserService
from banking_api.exceptions import UserNotFoundError

UserModel = get_user_model()

def test_create_user(db):
    """Test creating a new user."""
    user_service = UserService()
    user = user_service.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.check_password("password123")

def test_get_user(db):
    """Test getting a user by ID."""
    user_service = UserService()
    
    # Create a user
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the user
    retrieved_user = user_service.get_user(user.id)
    
    assert retrieved_user == user

def test_get_nonexistent_user(db):
    """Test getting a non-existent user."""
    user_service = UserService()
    
    with pytest.raises(UserNotFoundError):
        user_service.get_user(9999)

def test_update_user(db):
    """Test updating a user."""
    user_service = UserService()
    
    # Create a user
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Update the user
    updated_user = user_service.update_user(
        user.id,
        username="updateduser",
        email="updated@example.com"
    )
    
    assert updated_user.username == "updateduser"
    assert updated_user.email == "updated@example.com"

def test_update_nonexistent_user(db):
    """Test updating a non-existent user."""
    user_service = UserService()
    
    with pytest.raises(UserNotFoundError):
        user_service.update_user(
            9999,
            username="updateduser",
            email="updated@example.com"
        )

def test_delete_user(db):
    """Test deleting a user."""
    user_service = UserService()
    
    # Create a user
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Delete the user
    user_service.delete_user(user.id)
    
    # Verify the user is deleted
    with pytest.raises(UserModel.DoesNotExist):
        UserModel.objects.get(id=user.id)

def test_delete_nonexistent_user(db):
    """Test deleting a non-existent user."""
    user_service = UserService()
    
    with pytest.raises(UserNotFoundError):
        user_service.delete_user(9999)
