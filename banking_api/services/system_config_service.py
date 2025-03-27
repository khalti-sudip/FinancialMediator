"""
System Configuration service module for banking_api.

This service handles all system configuration business logic.
"""

from typing import Optional, Dict
from django.db import transaction
from banking_api.models import SystemConfig
from banking_api.exceptions import SystemConfigError

class SystemConfigService:
    """Service class for system configuration operations."""
    
    def get_config(self, key: str) -> Optional[Dict]:
        """
        Get a system configuration value by key.
        
        Args:
            key: The configuration key
            
        Returns:
            The configuration value as a dictionary
            
        Raises:
            SystemConfigError: If configuration retrieval fails
        """
        try:
            config = SystemConfig.objects.get(key=key)
            return {
                "key": config.key,
                "value": config.value,
                "description": config.description,
                "last_modified": config.last_modified
            }
        except SystemConfig.DoesNotExist:
            return None
        except Exception as e:
            raise SystemConfigError(f"Failed to get configuration: {str(e)}")
    
    def set_config(self, key: str, value: str, description: str = None) -> SystemConfig:
        """
        Set or update a system configuration value.
        
        Args:
            key: The configuration key
            value: The configuration value
            description: Description of the configuration (optional)
            
        Returns:
            The updated SystemConfig instance
            
        Raises:
            SystemConfigError: If configuration update fails
        """
        try:
            with transaction.atomic():
                config, created = SystemConfig.objects.update_or_create(
                    key=key,
                    defaults={
                        "value": value,
                        "description": description
                    }
                )
                return config
        except Exception as e:
            raise SystemConfigError(f"Failed to set configuration: {str(e)}")
    
    def get_all_configs(self) -> Dict[str, Dict]:
        """
        Get all system configurations.
        
        Returns:
            Dictionary of all configurations
            
        Raises:
            SystemConfigError: If configuration retrieval fails
        """
        try:
            configs = SystemConfig.objects.all()
            return {
                config.key: {
                    "value": config.value,
                    "description": config.description,
                    "last_modified": config.last_modified
                }
                for config in configs
            }
        except Exception as e:
            raise SystemConfigError(f"Failed to get all configurations: {str(e)}")
    
    def delete_config(self, key: str) -> None:
        """
        Delete a system configuration.
        
        Args:
            key: The configuration key to delete
            
        Raises:
            SystemConfigError: If configuration deletion fails
        """
        try:
            config = SystemConfig.objects.get(key=key)
            config.delete()
        except SystemConfig.DoesNotExist:
            raise SystemConfigError(f"Configuration {key} not found")
        except Exception as e:
            raise SystemConfigError(f"Failed to delete configuration: {str(e)}")
    
    def validate_config(self, key: str, value: str) -> bool:
        """
        Validate a system configuration value.
        
        Args:
            key: The configuration key
            value: The configuration value
            
        Returns:
            True if the configuration is valid, False otherwise
            
        Raises:
            SystemConfigError: If validation fails
        """
        try:
            config = self.get_config(key)
            if not config:
                return False
                
            # Add validation logic here
            return True
        except Exception as e:
            raise SystemConfigError(f"Failed to validate configuration: {str(e)}")
    
    def get_config_history(self, key: str, limit: int = 100) -> List[Dict]:
        """
        Get history of configuration changes.
        
        Args:
            key: The configuration key
            limit: Maximum number of history entries
            
        Returns:
            List of configuration history entries
            
        Raises:
            SystemConfigError: If history retrieval fails
        """
        try:
            configs = SystemConfig.objects.filter(key=key).order_by('-last_modified')[:limit]
            return [
                {
                    "key": config.key,
                    "value": config.value,
                    "description": config.description,
                    "last_modified": config.last_modified
                }
                for config in configs
            ]
        except Exception as e:
            raise SystemConfigError(f"Failed to get configuration history: {str(e)}")
