"""
Provider registry utility for managing financial institutions and providers.

This module provides a centralized registry for managing:
1. Provider types and implementations
2. Financial institution types
3. Provider instances and their status
4. Request routing and processing

The registry ensures consistent provider management and request handling.
"""

from typing import Dict, Type, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import threading

from ..base.provider import BaseProvider, BaseFinancialInstitution


class ProviderRegistry:
    """
    Registry for managing financial institutions and providers.
    
    Provides a centralized way to:
    - Register new providers and institutions
    - Retrieve providers by type
    - Process requests from institutions
    - Manage provider instances
    
    Usage:
    ```python
    # Register a new provider type
    registry = ProviderRegistry()
    registry.register_provider("bank", BankProvider)
    
    # Get a provider instance
    provider = registry.get_provider("bank")
    
    # Process a request
    result = registry.process_request(
        provider_type="bank",
        request_data={"amount": 100}
    )
    ```
    """
    
    def __init__(self):
        """
        Initialize the provider registry.
        
        Sets up:
        - Provider type registry
        - Institution type registry
        - Active instance tracking
        - Thread safety
        """
        self.providers: Dict[str, Type[BaseProvider]] = {}
        self.institutions: Dict[str, Type[BaseFinancialInstitution]] = {}
        self.active_instances: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    def register_provider(self, provider_type: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a new provider type.
        
        Args:
            provider_type: Unique identifier for the provider type
            provider_class: Provider implementation class
            
        Raises:
            ValueError: If provider type is already registered
            TypeError: If provider class doesn't implement BaseProvider
        """
        if not issubclass(provider_class, BaseProvider):
            raise TypeError("Provider class must implement BaseProvider")
            
        with self._lock:
            if provider_type in self.providers:
                raise ValueError(f"Provider type '{provider_type}' already registered")
                
            self.providers[provider_type] = provider_class
    
    def register_institution(self, institution_type: str, institution_class: Type[BaseFinancialInstitution]) -> None:
        """
        Register a new financial institution type.
        
        Args:
            institution_type: Unique identifier for the institution type
            institution_class: Institution implementation class
            
        Raises:
            ValueError: If institution type is already registered
            TypeError: If institution class doesn't implement BaseFinancialInstitution
        """
        if not issubclass(institution_class, BaseFinancialInstitution):
            raise TypeError("Institution class must implement BaseFinancialInstitution")
            
        with self._lock:
            if institution_type in self.institutions:
                raise ValueError(f"Institution type '{institution_type}' already registered")
                
            self.institutions[institution_type] = institution_class
    
    def get_provider(self, provider_type: str) -> Optional[BaseProvider]:
        """
        Get a provider instance by type.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            BaseProvider: Provider instance if available, None otherwise
        """
        with self._lock:
            provider_class = self.providers.get(provider_type)
            if not provider_class:
                return None
                
            instance = self.active_instances.get(provider_type)
            if not instance:
                instance = provider_class()
                self.active_instances[provider_type] = instance
                
            return instance
    
    def process_request(
        self,
        provider_type: str,
        request_data: Dict[str, Any],
        timeout: float = 30.0,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Process a request through a provider.
        
        Args:
            provider_type: Type of provider to use
            request_data: Request data
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            
        Returns:
            Dict: Response data from the provider
            
        Raises:
            ProviderError: If request processing fails
            TimeoutError: If request times out
            ValueError: If provider type is not registered
        """
        provider = self.get_provider(provider_type)
        if not provider:
            raise ValueError(f"Provider type '{provider_type}' not registered")
            
        for attempt in range(retries):
            try:
                response = provider.process_request(request_data, timeout=timeout)
                return response
                
            except TimeoutError as e:
                if attempt == retries - 1:
                    raise
                
            except Exception as e:
                if attempt == retries - 1:
                    raise ProviderError(f"Request failed: {str(e)}")
                
        raise ProviderError("Request failed after retries")
    
    def get_institution(self, institution_type: str) -> Optional[BaseFinancialInstitution]:
        """
        Get a financial institution instance by type.
        
        Args:
            institution_type: Institution type identifier
            
        Returns:
            BaseFinancialInstitution: Institution instance if available, None otherwise
        """
        with self._lock:
            institution_class = self.institutions.get(institution_type)
            if not institution_class:
                return None
                
            instance = self.active_instances.get(institution_type)
            if not instance:
                instance = institution_class()
                self.active_instances[institution_type] = instance
                
            return instance
    
    def get_provider_status(self, provider_type: str) -> Dict[str, Any]:
        """
        Get the status of a provider.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Dict: Provider status information
            
        Raises:
            ValueError: If provider type is not registered
        """
        provider = self.get_provider(provider_type)
        if not provider:
            raise ValueError(f"Provider type '{provider_type}' not registered")
            
        return {
            "status": provider.get_status(),
            "last_check": datetime.now().isoformat(),
            "type": provider_type,
            "is_active": provider.is_active()
        }
    
    def get_all_provider_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status information for all registered providers.
        
        Returns:
            Dict: Mapping of provider types to their status information
        """
        statuses = {}
        for provider_type in self.providers:
            try:
                status = self.get_provider_status(provider_type)
                statuses[provider_type] = status
            except Exception as e:
                statuses[provider_type] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.now().isoformat(),
                    "type": provider_type
                }
        return statuses

class ProviderError(Exception):
    """
    Base exception for provider-related errors.
    
    Attributes:
        message: Error message
        provider_type: Type of provider that failed
        request_data: Original request data
    """
    def __init__(self, message: str, provider_type: str = None, request_data: Dict[str, Any] = None):
        self.message = message
        self.provider_type = provider_type
        self.request_data = request_data
        super().__init__(message)

class TimeoutError(ProviderError):
    """
    Exception raised when a provider request times out.
    
    Attributes:
        message: Error message
        timeout: Timeout duration
        provider_type: Type of provider that timed out
    """
    def __init__(self, message: str, timeout: float, provider_type: str = None):
        self.timeout = timeout
        super().__init__(message, provider_type=provider_type)

class ConfigurationError(ProviderError):
    """
    Exception raised when provider configuration is invalid.
    
    Attributes:
        message: Error message
        provider_type: Type of provider with invalid config
        config: Invalid configuration
    """
    def __init__(self, message: str, provider_type: str, config: Dict[str, Any]):
        self.config = config
        super().__init__(message, provider_type=provider_type)

class AuthenticationError(ProviderError):
    """
    Exception raised when provider authentication fails.
    
    Attributes:
        message: Error message
        provider_type: Type of provider that failed authentication
        auth_data: Authentication data used
    """
    def __init__(self, message: str, provider_type: str, auth_data: Dict[str, Any]):
        self.auth_data = auth_data
        super().__init__(message, provider_type=provider_type)


# Create a global registry instance
registry = ProviderRegistry()

# Register providers and institutions
def register_all():
    """
    Register all available providers and institutions.
    """
    from ..financial_providers import payment_gateway
    from ..financial_institutions import bank
    
    registry.register_provider('payment_gateway', payment_gateway.PaymentGateway)
    registry.register_institution('bank', bank.Bank)

# Register all providers and institutions
register_all()
