"""
KYC Service Registry.

This module provides a registry for managing KYC providers and clients.
"""

from typing import Dict, Type, Any
from collections import defaultdict

from ..providers.base import BaseKYCProvider, BaseKYCClient


class KYCRegistry:
    """
    Registry for managing KYC providers and clients.
    
    Provides a centralized way to:
    - Register new KYC providers and clients
    - Retrieve providers by type
    - Process KYC verification requests
    """
    
    def __init__(self):
        self.providers: Dict[str, Type[BaseKYCProvider]] = {}
        self.clients: Dict[str, Type[BaseKYCClient]] = {}
        self.active_instances: Dict[str, Any] = {}
    
    def register_provider(self, provider_type: str, provider_class: Type[BaseKYCProvider]) -> None:
        """
        Register a new KYC provider type.
        
        Args:
            provider_type: Unique identifier for the provider type
            provider_class: Provider implementation class
        """
        self.providers[provider_type] = provider_class
    
    def register_client(self, client_type: str, client_class: Type[BaseKYCClient]) -> None:
        """
        Register a new KYC client type.
        
        Args:
            client_type: Unique identifier for the client type
            client_class: Client implementation class
        """
        self.clients[client_type] = client_class
    
    def get_provider(self, provider_type: str) -> Type[BaseKYCProvider]:
        """
        Get a KYC provider class by type.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Type[BaseKYCProvider]: The provider class
            
        Raises:
            KeyError: If provider type is not registered
        """
        return self.providers[provider_type]
    
    def get_client(self, client_type: str) -> Type[BaseKYCClient]:
        """
        Get a KYC client class by type.
        
        Args:
            client_type: Client type identifier
            
        Returns:
            Type[BaseKYCClient]: The client class
            
        Raises:
            KeyError: If client type is not registered
        """
        return self.clients[client_type]
    
    def create_provider_instance(
        self, 
        provider_type: str, 
        config: Dict[str, Any]
    ) -> BaseKYCProvider:
        """
        Create and initialize a KYC provider instance.
        
        Args:
            provider_type: Provider type identifier
            config: Provider configuration
            
        Returns:
            BaseKYCProvider: The initialized provider instance
        """
        provider_class = self.get_provider(provider_type)
        instance = provider_class()
        instance.initialize(config)
        return instance
    
    def create_client_instance(
        self, 
        client_type: str, 
        provider: BaseKYCProvider
    ) -> BaseKYCClient:
        """
        Create a KYC client instance.
        
        Args:
            client_type: Client type identifier
            provider: Associated KYC provider instance
            
        Returns:
            BaseKYCClient: The client instance
        """
        client_class = self.get_client(client_type)
        return client_class(provider)
    
    def process_verification(
        self, 
        provider_type: str, 
        client_type: str, 
        entity_id: str,
        subject_type: str,
        subject_id: str,
        verification_type: str,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a KYC verification request.
        
        Args:
            provider_type: Type of the KYC provider
            client_type: Type of the KYC client
            entity_id: ID of the requesting entity
            subject_type: Type of the subject being verified
            subject_id: ID of the subject
            verification_type: Type of verification
            request_data: Request-specific data
            
        Returns:
            Dict: Processed verification response
        """
        # Create provider instance
        provider_config = request_data.get('provider_config', {})
        provider = self.create_provider_instance(provider_type, provider_config)
        
        # Create client instance
        client = self.create_client_instance(client_type, provider)
        
        # Create and process request
        request = client.create_verification_request(
            entity_id=entity_id,
            subject_type=subject_type,
            subject_id=subject_id,
            verification_type=verification_type,
            data=request_data
        )
        
        response = provider.process_verification(request)
        
        return {
            'request_id': response.request_id,
            'status': response.status,
            'verification_score': response.verification_score,
            'is_verified': response.is_verified,
            'details': response.details,
            'error': response.error
        }

# Create a global registry instance
kyc_registry = KYCRegistry()

# Register providers and clients
def register_all():
    """
    Register all available KYC providers and clients.
    """
    from ..providers import sample_kyc
    
    kyc_registry.register_provider('sample', sample_kyc.SampleKYCProvider)
    kyc_registry.register_client('sample', sample_kyc.SampleKYCClient)

# Register all providers and clients
register_all()
