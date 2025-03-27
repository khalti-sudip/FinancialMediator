"""
Tests for the error handling utilities.
"""

import pytest
from core.utils.errors import (
    FinancialMediatorError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    ProviderError,
    error_handler,
    format_error_response,
    capture_error_context,
    track_user_operation,
    track_api_request
)

def test_financial_mediator_error():
    """Test the base FinancialMediatorError."""
    error = FinancialMediatorError("Test error", code="TEST_ERROR", context={"key": "value"})
    assert str(error) == "Test error"
    assert error.code == "TEST_ERROR"
    assert error.context == {"key": "value"}

def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Invalid field", field="username", context={"key": "value"})
    assert str(error) == "Invalid field"
    assert error.code == "VALIDATION_ERROR"
    assert error.field == "username"
    assert error.context == {"key": "value"}

def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid credentials", context={"key": "value"})
    assert str(error) == "Invalid credentials"
    assert error.code == "AUTHENTICATION_ERROR"
    assert error.context == {"key": "value"}

def test_authorization_error():
    """Test AuthorizationError."""
    error = AuthorizationError("Permission denied", context={"key": "value"})
    assert str(error) == "Permission denied"
    assert error.code == "AUTHORIZATION_ERROR"
    assert error.context == {"key": "value"}

def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError("Rate limit exceeded", limit=100, window=60, context={"key": "value"})
    assert str(error) == "Rate limit exceeded"
    assert error.code == "RATE_LIMIT_ERROR"
    assert error.limit == 100
    assert error.window == 60
    assert error.context == {"key": "value"}

def test_provider_error():
    """Test ProviderError."""
    error = ProviderError("Provider error", provider="test_provider", context={"key": "value"})
    assert str(error) == "Provider error"
    assert error.code == "PROVIDER_ERROR"
    assert error.provider == "test_provider"
    assert error.context == {"key": "value"}

def test_error_handler():
    """Test the error handler decorator."""
    @error_handler
    def test_function():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        test_function()

def test_format_error_response():
    """Test error response formatting."""
    error = FinancialMediatorError("Test error", code="TEST_ERROR", context={"key": "value"})
    response = format_error_response(error)
    assert response == {
        "error": {
            "code": "TEST_ERROR",
            "message": "Test error",
            "context": {"key": "value"}
        }
    }

def test_capture_error_context():
    """Test error context capture."""
    error = ValueError("Test error")
    context = {"key": "value"}
    capture_error_context(error, context)

def test_track_user_operation():
    """Test user operation tracking."""
    user_id = "123"
    operation = "test_operation"
    track_user_operation(user_id, operation)

def test_track_api_request():
    """Test API request tracking."""
    # Mock request and response objects
    class MockRequest:
        path = "/test"
        method = "GET"
    
    class MockResponse:
        status_code = 200
    
    request = MockRequest()
    response = MockResponse()
    
    track_api_request(request, response)
