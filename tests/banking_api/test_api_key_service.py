"""
Tests for the API key service.
"""

import pytest
from django.contrib.auth import get_user_model
from banking_api.services.api_key_service import APIKeyService
from banking_api.exceptions import APIKeyError

UserModel = get_user_model()

def test_generate_api_key(db):
    """Test generating a new API key."""
    api_key_service = APIKeyService()
    
    # Create a user
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Generate API key
    api_key = api_key_service.generate_api_key(
        user_id=user.id,
        name="test_api_key"
    )
    
    assert api_key.user == user
    assert api_key.name == "test_api_key"
    assert api_key.is_active
    assert not api_key.expired

def test_get_api_key(db):
    """Test getting an API key by ID."""
    api_key_service = APIKeyService()
    
    # Create a user and API key
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    api_key = api_key_service.generate_api_key(
        user_id=user.id,
        name="test_api_key"
    )
    
    # Get the API key
    retrieved_key = api_key_service.get_api_key(api_key.id)
    
    assert retrieved_key == api_key

def test_get_nonexistent_api_key(db):
    """Test getting a non-existent API key."""
    api_key_service = APIKeyService()
    
    with pytest.raises(APIKeyError):
        api_key_service.get_api_key(9999)

def test_update_api_key(db):
    """Test updating an API key."""
    api_key_service = APIKeyService()
    
    # Create a user and API key
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    api_key = api_key_service.generate_api_key(
        user_id=user.id,
        name="test_api_key"
    )
    
    # Update the API key
    updated_key = api_key_service.update_api_key(
        api_key.id,
        name="updated_api_key",
        is_active=False
    )
    
    assert updated_key.name == "updated_api_key"
    assert not updated_key.is_active

def test_validate_api_key(db):
    """Test validating an API key."""
    api_key_service = APIKeyService()
    
    # Create a user and API key
    user = UserModel.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    api_key = api_key_service.generate_api_key(
        user_id=user.id,
        name="test_api_key"
    )
    
    # Validate the API key
    assert api_key_service.validate_api_key(api_key.value)
    
    # Deactivate the API key and validate again
    updated_key = api_key_service.update_api_key(
        api_key.id,
        is_active=False
    )
    assert not api_key_service.validate_api_key(updated_key.value)
