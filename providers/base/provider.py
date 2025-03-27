"""
Base classes for financial providers and institutions.

This module provides the abstract base classes for implementing financial providers
and institutions. It defines the interface that all implementations must follow.

Key Features:
1. Standardized request/response handling
2. Consistent error handling
3. Provider configuration management
4. Request validation and processing
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseProvider(ABC):
    """
    Abstract base class for all providers.
    
    Defines the interface that all provider implementations must follow.
    
    Provider States:
    - INITIALIZING: Provider is being initialized
    - READY: Provider is ready to process requests
    - ERROR: Provider encountered an error
    - OFFLINE: Provider is temporarily offline
    - DISABLED: Provider is disabled
    """
    
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    ERROR = "ERROR"
    OFFLINE = "OFFLINE"
    DISABLED = "DISABLED"
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration
            
        Raises:
            ValueError: If required configuration is missing
            ConfigurationError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the provider.
        
        Returns:
            bool: True if authentication was successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def process_request(self, request_data: Dict[str, Any], timeout: float = 30.0) -> Dict[str, Any]:
        """
        Process a request from a financial institution.
        
        Args:
            request_data: Request data containing:
                - institution_id: ID of the requesting institution
                - request_type: Type of request
                - payload: Request payload data
                - metadata: Additional metadata
            timeout: Request timeout in seconds
            
        Returns:
            Dict: Response data containing:
                - status: Response status
                - data: Response payload
                - timestamp: Response timestamp
                - metadata: Additional metadata
            
        Raises:
            ProviderError: If request processing fails
            TimeoutError: If request times out
        """
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """
        Get the current status of the provider.
        
        Returns:
            str: Current provider status (INITIALIZING, READY, etc.)
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """
        Check if the provider is active and ready to process requests.
        
        Returns:
            bool: True if provider is active, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_request_types(self) -> List[str]:
        """
        Get list of supported request types.
        
        Returns:
            List[str]: List of supported request types
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider.
        
        Returns:
            Dict: Provider information containing:
                - name: Provider name
                - version: Provider version
                - status: Current status
                - supported_types: List of supported request types
                - metadata: Additional provider metadata
        """
        pass

class BaseFinancialInstitution(ABC):
    """
    Abstract base class for financial institutions.
    
    Defines the interface that all institution implementations must follow.
    
    Institution States:
    - INITIALIZING: Institution is being initialized
    - ACTIVE: Institution is active
    - SUSPENDED: Institution is suspended
    - TERMINATED: Institution is terminated
    """
    
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    
    @abstractmethod
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the financial institution.
        
        Args:
            config: Institution-specific configuration
            
        Raises:
            ValueError: If required configuration is missing
            ConfigurationError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def create_request(
        self, 
        provider_type: str, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a request to a provider.
        
        Args:
            provider_type: Type of provider to request
            request_data: Request data
            
        Returns:
            Dict: Formatted request data
            
        Raises:
            ValueError: If request data is invalid
        """
        pass
    
    @abstractmethod
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a response from a provider.
        
        Args:
            response_data: Response data from provider
            
        Returns:
            Dict: Processed response data
            
        Raises:
            ValueError: If response data is invalid
        """
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """
        Get the current status of the institution.
        
        Returns:
            str: Current institution status (INITIALIZING, ACTIVE, etc.)
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """
        Check if the institution is active and ready to process requests.
        
        Returns:
            bool: True if institution is active, False otherwise
        """
        pass
    
    @abstractmethod
    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported provider types.
        
        Returns:
            List[str]: List of supported provider types
        """
        pass
    
    @abstractmethod
    def get_institution_info(self) -> Dict[str, Any]:
        """
        Get information about the institution.
        
        Returns:
            Dict: Institution information containing:
                - name: Institution name
                - type: Institution type
                - status: Current status
                - supported_providers: List of supported provider types
                - metadata: Additional institution metadata
        """
        pass
