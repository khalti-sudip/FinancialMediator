"""
Base provider interface and abstract classes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProviderRequest:
    """Base class for provider requests."""
    request_id: str
    timestamp: datetime
    institution_id: str
    provider_id: str
    data: Dict[str, Any]

@dataclass
class ProviderResponse:
    """Base class for provider responses."""
    request_id: str
    timestamp: datetime
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None


class BaseProvider(ABC):
    """
    Abstract base class for all providers.
    
    Defines the interface that all provider implementations must follow.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the provider.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: ProviderRequest) -> bool:
        """
        Validate a provider request.
        
        Args:
            request: The request to validate
            
        Returns:
            bool: True if request is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def process_request(self, request: ProviderRequest) -> ProviderResponse:
        """
        Process a provider request.
        
        Args:
            request: The request to process
            
        Returns:
            ProviderResponse: The response from the provider
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the provider.
        
        Returns:
            Dict: Provider status information
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, data: Dict[str, Any]) -> ProviderResponse:
        """
        Handle incoming webhook from the provider.
        
        Args:
            data: Webhook data
            
        Returns:
            ProviderResponse: Response to the webhook
        """
        pass


class BaseFinancialInstitution(ABC):
    """
    Abstract base class for financial institutions.
    
    Represents institutions that can send requests to providers.
    """
    
    @abstractmethod
    def get_institution_id(self) -> str:
        """
        Get the unique identifier for this institution.
        
        Returns:
            str: Institution identifier
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate institution credentials.
        
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    def create_request(
        self, 
        provider_id: str, 
        request_data: Dict[str, Any]
    ) -> ProviderRequest:
        """
        Create a request to be sent to a provider.
        
        Args:
            provider_id: ID of the target provider
            request_data: Request data
            
        Returns:
            ProviderRequest: The created request
        """
        pass
    
    @abstractmethod
    def process_response(self, response: ProviderResponse) -> Dict[str, Any]:
        """
        Process a response from a provider.
        
        Args:
            response: The provider response
            
        Returns:
            Dict: Processed response data
        """
        pass
