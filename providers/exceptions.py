"""Custom exceptions for the providers app."""

from banking_api.exceptions import FinancialMediatorError

class ProviderError(FinancialMediatorError):
    """Base exception for provider-related errors."""
    pass

class ProviderNotFoundError(ProviderError):
    """Raised when a provider is not found."""
    pass

class ProviderKeyError(ProviderError):
    """Base exception for provider key-related errors."""
    pass

class ProviderKeyNotFoundError(ProviderKeyError):
    """Raised when a provider key is not found."""
    pass

class ProviderWebhookError(ProviderError):
    """Base exception for provider webhook-related errors."""
    pass

class ProviderWebhookNotFoundError(ProviderWebhookError):
    """Raised when a provider webhook is not found."""
    pass
