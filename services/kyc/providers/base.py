"""
Base KYC provider interface and abstract classes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class KYCRequestData:
    """Base class for KYC request data."""
    request_id: str
    timestamp: datetime
    entity_id: str
    subject_type: str
    subject_id: str
    verification_type: str
    data: Dict[str, Any]

@dataclass
class KYCResponse:
    """Base class for KYC response."""
    request_id: str
    timestamp: datetime
    status: str
    verification_score: float
    is_verified: bool
    details: Dict[str, Any]
    error: Optional[str] = None


class BaseKYCProvider(ABC):
    """
    Abstract base class for KYC providers.
    
    Defines the interface that all KYC provider implementations must follow.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the KYC provider with configuration.
        
        Args:
            config: Provider-specific configuration
        """
        pass
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the KYC provider.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: KYCRequestData) -> bool:
        """
        Validate a KYC request.
        
        Args:
            request: The request to validate
            
        Returns:
            bool: True if request is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def process_verification(
        self, 
        request: KYCRequestData
    ) -> KYCResponse:
        """
        Process a KYC verification request.
        
        Args:
            request: The verification request
            
        Returns:
            KYCResponse: The verification response
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the KYC provider.
        
        Returns:
            Dict: Provider status information
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, data: Dict[str, Any]) -> KYCResponse:
        """
        Handle incoming webhook from the KYC provider.
        
        Args:
            data: Webhook data
            
        Returns:
            KYCResponse: Response to the webhook
        """
        pass
    
    @abstractmethod
    def get_supported_verification_types(self) -> list[str]:
        """
        Get the list of supported verification types.
        
        Returns:
            list[str]: List of supported verification types
        """
        pass


class BaseKYCClient(ABC):
    """
    Abstract base class for KYC client implementations.
    
    Provides a standardized interface for making KYC verification requests.
    """
    
    def __init__(self, provider: BaseKYCProvider):
        self.provider = provider
    
    @abstractmethod
    def create_verification_request(
        self,
        entity_id: str,
        subject_type: str,
        subject_id: str,
        verification_type: str,
        data: Dict[str, Any]
    ) -> KYCRequestData:
        """
        Create a new KYC verification request.
        
        Args:
            entity_id: ID of the requesting entity
            subject_type: Type of the subject being verified
            subject_id: ID of the subject
            verification_type: Type of verification
            data: Request-specific data
            
        Returns:
            KYCRequestData: The created request
        """
        pass
    
    @abstractmethod
    def get_verification_status(self, request_id: str) -> KYCResponse:
        """
        Get the status of a KYC verification request.
        
        Args:
            request_id: ID of the verification request
            
        Returns:
            KYCResponse: The verification response
        """
        pass
    
    @abstractmethod
    def cancel_verification(self, request_id: str) -> bool:
        """
        Cancel a pending KYC verification request.
        
        Args:
            request_id: ID of the verification request
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        pass
