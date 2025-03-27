"""
Base classes for KYC providers and clients.

This module provides the abstract base classes for implementing KYC providers
and their corresponding clients. It defines the interface that all KYC
implementations must follow.

Key Features:
1. Standardized verification types
2. Consistent status handling
3. Common error handling
4. Provider configuration management
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseKYCProvider(ABC):
    """
    Abstract base class for KYC providers.
    
    Defines the interface that all KYC provider implementations must follow.
    
    Verification Types:
    - DOCUMENT: Document verification
    - FACE: Face verification
    - ADDRESS: Address verification
    - BACKGROUND: Background check
    - COMPLIANCE: Regulatory compliance check
    
    Status Types:
    - PENDING: Verification pending
    - VERIFIED: Successfully verified
    - REJECTED: Verification failed
    - EXPIRED: Verification expired
    - REVOKED: Verification revoked
    """
    
    DOCUMENT = "DOCUMENT"
    FACE = "FACE"
    ADDRESS = "ADDRESS"
    BACKGROUND = "BACKGROUND"
    COMPLIANCE = "COMPLIANCE"
    
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the KYC provider with configuration.
        
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
        Authenticate with the KYC provider.
        
        Returns:
            bool: True if authentication was successful, False otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    def verify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a KYC request.
        
        Args:
            data: Verification data containing:
                - verification_type: Type of verification (DOCUMENT, FACE, etc.)
                - user_data: User-specific information
                - document_data: Document information (if applicable)
                - face_data: Face verification data (if applicable)
                - address_data: Address verification data (if applicable)
                
        Returns:
            Dict: Verification result containing:
                - status: Verification status (PENDING, VERIFIED, etc.)
                - verification_id: Unique verification identifier
                - details: Verification details
                - timestamp: Timestamp of verification
                
        Raises:
            ValidationError: If verification data is invalid
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def get_status(self, verification_id: str) -> Dict[str, Any]:
        """
        Get the current status of a verification request.
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            Dict: Verification status containing:
                - status: Current verification status
                - details: Status details
                - timestamp: Last update timestamp
                
        Raises:
            NotFoundError: If verification ID is not found
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def cancel_verification(self, verification_id: str) -> bool:
        """
        Cancel an ongoing verification request.
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            bool: True if cancellation was successful
            
        Raises:
            NotFoundError: If verification ID is not found
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def get_supported_verifications(self) -> List[str]:
        """
        Get list of supported verification types.
        
        Returns:
            List[str]: List of supported verification types
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the KYC provider.
        
        Returns:
            Dict: Provider information containing:
                - name: Provider name
                - version: Provider API version
                - supported_verifications: List of supported verification types
                - status: Current provider status
                
        Raises:
            ProviderError: If provider information cannot be retrieved
        """
        pass

class BaseKYCClient(ABC):
    """
    Abstract base class for KYC provider clients.
    
    Defines the interface that all KYC client implementations must follow.
    
    The client handles:
    1. Provider communication
    2. Error handling
    3. Response parsing
    4. Status tracking
    """
    
    @abstractmethod
    def __init__(self, provider: BaseKYCProvider):
        """
        Initialize the KYC client.
        
        Args:
            provider: KYC provider instance
        """
        pass
    
    @abstractmethod
    def verify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a KYC request through the provider.
        
        Args:
            data: Verification data
            
        Returns:
            Dict: Verification result
            
        Raises:
            ValidationError: If verification data is invalid
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def get_status(self, verification_id: str) -> Dict[str, Any]:
        """
        Get the current status of a verification request.
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            Dict: Verification status
            
        Raises:
            NotFoundError: If verification ID is not found
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def cancel_verification(self, verification_id: str) -> bool:
        """
        Cancel an ongoing verification request.
        
        Args:
            verification_id: Unique verification identifier
            
        Returns:
            bool: True if cancellation was successful
            
        Raises:
            NotFoundError: If verification ID is not found
            ProviderError: If provider-specific error occurs
        """
        pass
    
    @abstractmethod
    def get_supported_verifications(self) -> List[str]:
        """
        Get list of supported verification types.
        
        Returns:
            List[str]: List of supported verification types
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the KYC provider.
        
        Returns:
            Dict: Provider information
            
        Raises:
            ProviderError: If provider information cannot be retrieved
        """
        pass
