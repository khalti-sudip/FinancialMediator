"""
Custom exceptions for the banking_api application.

This module defines custom exceptions for different error scenarios.
"""

from core.utils.errors import FinancialMediatorError

class UserNotFoundError(FinancialMediatorError):
    """Raised when a user is not found."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="USER_NOT_FOUND", context=context)

class InvalidCredentialsError(FinancialMediatorError):
    """Raised when credentials are invalid."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="INVALID_CREDENTIALS", context=context)

class InsufficientBalanceError(FinancialMediatorError):
    """Raised when a user has insufficient balance."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="INSUFFICIENT_BALANCE", context=context)

class TransactionError(FinancialMediatorError):
    """Raised when a transaction fails."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="TRANSACTION_ERROR", context=context)

class ProviderError(FinancialMediatorError):
    """Raised when a provider operation fails."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="PROVIDER_ERROR", context=context)

class KYCError(FinancialMediatorError):
    """Raised when a KYC operation fails."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="KYC_ERROR", context=context)

class RateLimitError(FinancialMediatorError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str, limit: int, window: int, context: dict = None):
        super().__init__(message, code="RATE_LIMIT_ERROR", context=context)
        self.limit = limit
        self.window = window
