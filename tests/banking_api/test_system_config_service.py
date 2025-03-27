"""
Tests for the system configuration service.
"""

import pytest
from django.contrib.auth import get_user_model
from banking_api.services.system_config_service import SystemConfigService
from banking_api.exceptions import SystemConfigError

UserModel = get_user_model()

def test_set_and_get_config(db):
    """Test setting and getting a configuration."""
    system_config_service = SystemConfigService()
    
    # Set configuration
    config = system_config_service.set_config(
        key="test_config",
        value="test_value",
        description="Test configuration"
    )
    
    assert config.key == "test_config"
    assert config.value == "test_value"
    assert config.description == "Test configuration"
    
    # Get configuration
    retrieved_config = system_config_service.get_config("test_config")
    assert retrieved_config["value"] == "test_value"
    assert retrieved_config["description"] == "Test configuration"

def test_get_nonexistent_config(db):
    """Test getting a non-existent configuration."""
    system_config_service = SystemConfigService()
    
    config = system_config_service.get_config("nonexistent_config")
    assert config is None

def test_update_config(db):
    """Test updating a configuration."""
    system_config_service = SystemConfigService()
    
    # Set initial configuration
    config = system_config_service.set_config(
        key="test_config",
        value="initial_value",
        description="Initial configuration"
    )
    
    # Update configuration
    updated_config = system_config_service.set_config(
        key="test_config",
        value="updated_value",
        description="Updated configuration"
    )
    
    assert updated_config.value == "updated_value"
    assert updated_config.description == "Updated configuration"

def test_get_all_configs(db):
    """Test getting all configurations."""
    system_config_service = SystemConfigService()
    
    # Set multiple configurations
    system_config_service.set_config(
        key="config1",
        value="value1",
        description="Config 1"
    )
    system_config_service.set_config(
        key="config2",
        value="value2",
        description="Config 2"
    )
    
    # Get all configurations
    configs = system_config_service.get_all_configs()
    
    assert len(configs) == 2
    assert configs["config1"]["value"] == "value1"
    assert configs["config2"]["value"] == "value2"

def test_delete_config(db):
    """Test deleting a configuration."""
    system_config_service = SystemConfigService()
    
    # Set configuration
    config = system_config_service.set_config(
        key="test_config",
        value="test_value",
        description="Test configuration"
    )
    
    # Delete configuration
    system_config_service.delete_config("test_config")
    
    # Verify deletion
    with pytest.raises(SystemConfigError):
        system_config_service.get_config("test_config")

def test_validate_config(db):
    """Test validating a configuration."""
    system_config_service = SystemConfigService()
    
    # Set configuration
    config = system_config_service.set_config(
        key="test_config",
        value="test_value",
        description="Test configuration"
    )
    
    # Validate configuration
    assert system_config_service.validate_config("test_config", "test_value")
    
    # Update configuration and validate again
    system_config_service.set_config(
        key="test_config",
        value="new_value",
        description="Updated configuration"
    )
    assert not system_config_service.validate_config("test_config", "test_value")
