"""
Provider registry for managing financial institutions and providers.
"""

from typing import Dict, Type, Any
from collections import defaultdict

from ..base.provider import BaseProvider, BaseFinancialInstitution


class ProviderRegistry:
    """
    Registry for managing financial institutions and providers.
    
    Provides a centralized way to:
    - Register new providers and institutions
    - Retrieve providers by type
    - Process requests from institutions
    """
    
    def __init__(self):
        self.providers: Dict[str, Type[BaseProvider]] = {}
        self.institutions: Dict[str, Type[BaseFinancialInstitution]] = {}
        self.active_instances: Dict[str, Any] = {}
    
    def register_provider(self, provider_type: str, provider_class: Type[BaseProvider]) -> None:
        """
        Register a new provider type.
        
        Args:
            provider_type: Unique identifier for the provider type
            provider_class: Provider implementation class
        """
        self.providers[provider_type] = provider_class
    
    def register_institution(
        self, 
        institution_type: str, 
        institution_class: Type[BaseFinancialInstitution]
    ) -> None:
        """
        Register a new financial institution type.
        
        Args:
            institution_type: Unique identifier for the institution type
            institution_class: Institution implementation class
        """
        self.institutions[institution_type] = institution_class
    
    def get_provider(self, provider_type: str) -> Type[BaseProvider]:
        """
        Get a provider class by type.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Type[BaseProvider]: The provider class
            
        Raises:
            KeyError: If provider type is not registered
        """
        return self.providers[provider_type]
    
    def get_institution(self, institution_type: str) -> Type[BaseFinancialInstitution]:
        """
        Get an institution class by type.
        
        Args:
            institution_type: Institution type identifier
            
        Returns:
            Type[BaseFinancialInstitution]: The institution class
            
        Raises:
            KeyError: If institution type is not registered
        """
        return self.institutions[institution_type]
    
    def create_provider_instance(
        self, 
        provider_type: str, 
        config: Dict[str, Any]
    ) -> BaseProvider:
        """
        Create and initialize a provider instance.
        
        Args:
            provider_type: Provider type identifier
            config: Provider configuration
            
        Returns:
            BaseProvider: The initialized provider instance
        """
        provider_class = self.get_provider(provider_type)
        instance = provider_class()
        instance.initialize(config)
        return instance
    
    def create_institution_instance(
        self, 
        institution_type: str, 
        config: Dict[str, Any]
    ) -> BaseFinancialInstitution:
        """
        Create a financial institution instance.
        
        Args:
            institution_type: Institution type identifier
            config: Institution configuration
            
        Returns:
            BaseFinancialInstitution: The institution instance
        """
        institution_class = self.get_institution(institution_type)
        return institution_class(config)
    
    def process_request(
        self, 
        institution_type: str, 
        provider_type: str, 
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a request from a financial institution to a provider.
        
        Args:
            institution_type: Type of the requesting institution
            provider_type: Type of the target provider
            request_data: Request data
            
        Returns:
            Dict: Processed response data
        """
        # Create institution instance
        institution = self.create_institution_instance(institution_type, request_data)
        
        # Create provider instance
        provider_config = request_data.get('provider_config', {})
        provider = self.create_provider_instance(provider_type, provider_config)
        
        # Process request
        request = institution.create_request(provider_type, request_data)
        response = provider.process_request(request)
        
        return institution.process_response(response)

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
