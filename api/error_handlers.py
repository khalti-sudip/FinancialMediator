"""
Error Handlers for Financial Mediator API.

This module defines custom exception handlers and error responses for the API.
It includes handlers for:
- API-specific exceptions
- Provider integration errors
- Authentication/Authorization errors
- Validation errors
- Rate limiting errors
"""

from typing import Dict, Any, Type, Union
from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
import logging

# Configure logger for error tracking
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "API_ERROR"

class ProviderError(APIError):
    """Exception raised when a provider integration fails."""
    
    def __init__(self, message: str = "Error communicating with the financial service provider"):
        super().__init__(message, status_code=502, error_code="PROVIDER_ERROR")

class RateLimitExceeded(APIError):
    """Exception raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded. Please try again later"):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")

class InvalidTransaction(APIError):
    """Exception raised for invalid transaction requests."""
    
    def __init__(self, message: str = "Invalid transaction request"):
        super().__init__(message, status_code=400, error_code="INVALID_TRANSACTION")

def register_error_handlers(app):
    """Register error handlers for the Flask application."""

    @app.errorhandler(APIError)
    def handle_api_error(error: APIError) -> tuple[Dict[str, Any], int]:
        """Handle custom API errors."""
        response = {"error": error.error_code, "message": error.message}
        return jsonify(response), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> tuple[Dict[str, Any], int]:
        """Handle Marshmallow validation errors."""
        response = {
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": error.messages,
        }
        return jsonify(response), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException) -> tuple[Dict[str, Any], int]:
        """Handle HTTP exceptions."""
        response = {"error": error.name, "message": error.description}
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error: Exception) -> tuple[Dict[str, Any], int]:
        """Handle any unhandled exceptions."""
        # Log the error here
        app.logger.error(f"Unhandled error: {str(error)}", exc_info=True)

        response = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        }
        return jsonify(response), 500

    @app.errorhandler(404)
    def handle_404(error: Exception) -> tuple[Dict[str, Any], int]:
        """Handle 404 Not Found errors."""
        response = {
            "error": "NOT_FOUND",
            "message": "The requested resource was not found",
        }
        return jsonify(response), 404

    @app.errorhandler(500)
    def handle_500(error: Exception) -> tuple[Dict[str, Any], int]:
        """Handle 500 Internal Server Error."""
        # Log the internal server error
        app.logger.error(f"Internal Server Error: {str(error)}", exc_info=True)

        response = {
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
        }
        return jsonify(response), 500

# Common error classes
class ResourceNotFoundError(APIError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="RESOURCE_NOT_FOUND")


class AuthenticationError(APIError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(APIError):
    """Raised when user is not authorized to perform an action."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")


class ValidationError(APIError):
    """Raised when request validation fails."""

    def __init__(self, message: str = "Validation failed", details: Dict = None):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")
        self.details = details
