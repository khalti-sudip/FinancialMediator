"""
Error handling utilities for FinancialMediator.

This module provides comprehensive error handling capabilities, including:
1. Custom error classes
2. Error handling decorators
3. Error response formatting
4. Exception context management
"""

import logging
from typing import Callable, TypeVar, ParamSpec, Any
from opentelemetry import trace
from opentelemetry.trace import Span
from opentelemetry.sdk._logs.severity import SeverityNumber
from core.utils.logging import get_logger
from core.sentry import capture_exception, set_user, set_context, set_tag, add_breadcrumb

T = TypeVar('T')
P = ParamSpec('P')

# Get the global tracer
tracer = trace.get_tracer(__name__)

class FinancialMediatorError(Exception):
    """Base class for all FinancialMediator errors."""
    def __init__(self, message: str, code: str = None, context: dict = None):
        super().__init__(message)
        self.code = code or "UNKNOWN_ERROR"
        self.context = context or {}

class ValidationError(FinancialMediatorError):
    """Raised for validation errors."""
    def __init__(self, message: str, field: str = None, context: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", context=context)
        self.field = field

class AuthenticationError(FinancialMediatorError):
    """Raised for authentication errors."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="AUTHENTICATION_ERROR", context=context)

class AuthorizationError(FinancialMediatorError):
    """Raised for authorization errors."""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message, code="AUTHORIZATION_ERROR", context=context)

class RateLimitError(FinancialMediatorError):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str, limit: int, window: int, context: dict = None):
        super().__init__(message, code="RATE_LIMIT_ERROR", context=context)
        self.limit = limit
        self.window = window

class ProviderError(FinancialMediatorError):
    """Raised for external provider errors."""
    def __init__(self, message: str, provider: str, context: dict = None):
        super().__init__(message, code="PROVIDER_ERROR", context=context)
        self.provider = provider

def error_handler(func: Callable[P, T]) -> Callable[P, T]:
    """
    Decorator to handle and log errors in a function.
    
    Args:
        func: The function to wrap
    
    Returns:
        Wrapped function with error handling
    """
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger = get_logger(func.__module__)
        with tracer.start_as_current_span(func.__name__) as span:
            try:
                return func(*args, **kwargs)
            except FinancialMediatorError as e:
                span.set_status(trace.StatusCode.ERROR)
                span.set_attribute("error.code", e.code)
                span.set_attribute("error.message", str(e))
                for key, value in e.context.items():
                    span.set_attribute(f"error.context.{key}", value)
                
                log_error(
                    logger,
                    f"{e.code}: {str(e)}",
                    exception=e,
                    attributes={
                        "error_code": e.code,
                        "context": e.context
                    }
                )
                
                # Capture in Sentry
                capture_exception(e)
                set_tag("error_code", e.code)
                set_context("error_context", e.context)
                
                raise
            except Exception as e:
                span.set_status(trace.StatusCode.ERROR)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                
                log_error(
                    logger,
                    f"Unexpected error: {str(e)}",
                    exception=e,
                    attributes={
                        "error_type": type(e).__name__
                    }
                )
                
                # Capture in Sentry
                capture_exception(e)
                set_tag("error_type", type(e).__name__)
                
                raise
    return wrapper

def format_error_response(error: Exception) -> dict:
    """
    Format an error response for API endpoints.
    
    Args:
        error: The exception to format
    
    Returns:
        Dictionary containing error information
    """
    if isinstance(error, FinancialMediatorError):
        return {
            "error": {
                "code": error.code,
                "message": str(error),
                "context": error.context
            }
        }
    else:
        return {
            "error": {
                "code": "UNKNOWN_ERROR",
                "message": "An unexpected error occurred",
                "context": {}
            }
        }

def capture_error_context(error: Exception, context: dict) -> None:
    """
    Capture additional context about an error.
    
    Args:
        error: The exception
        context: Additional context information
    """
    logger = get_logger(error.__class__.__module__)
    log_error(
        logger,
        f"Additional context for error: {str(error)}",
        exception=error,
        attributes=context
    )
    
    # Capture in Sentry
    capture_exception(error)
    set_context("error_context", context)

def track_user_operation(user_id: str, operation: str, success: bool = True) -> None:
    """
    Track a user operation in Sentry.
    
    Args:
        user_id: The user's ID
        operation: The operation being performed
        success: Whether the operation was successful
    """
    set_user(user_id)
    add_breadcrumb(
        category="user_operation",
        message=f"User {user_id} performed {operation}",
        level="info" if success else "error"
    )

def track_api_request(request: Any, response: Any) -> None:
    """
    Track an API request in Sentry.
    
    Args:
        request: The request object
        response: The response object
    """
    add_breadcrumb(
        category="api",
        message=f"API request to {request.path}",
        level="info"
    )
    set_context("api_request", {
        "path": request.path,
        "method": request.method,
        "status_code": response.status_code
    })
