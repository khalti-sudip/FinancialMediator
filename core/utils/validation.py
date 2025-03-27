"""
Validation utilities for FinancialMediator.

This module provides reusable validation functions for common operations across the application.
"""

from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime
from decimal import Decimal
import logging
from opentelemetry import trace

# Get the global tracer
tracer = trace.get_tracer(__name__)

class ValidationError(Exception):
    """
    Exception raised for validation errors.
    
    Attributes:
        message -- explanation of the error
        fields -- list of fields that failed validation
    """
    
    def __init__(self, message: str, fields: Optional[List[str]] = None):
        """
        Initialize a ValidationError.
        
        Args:
            message: Error message
            fields: List of fields that failed validation
        """
        self.message = message
        self.fields = fields or []
        super().__init__(message)

def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If email is invalid
    """
    with tracer.start_as_current_span("validate_email") as span:
        span.set_attribute("email", email)
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email address", ["email"])
            
        return True

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If phone number is invalid
    """
    with tracer.start_as_current_span("validate_phone") as span:
        span.set_attribute("phone", phone)
        
        pattern = r'^\+?[1-9]\d{1,14}$'
        if not re.match(pattern, phone):
            raise ValidationError("Invalid phone number", ["phone"])
            
        return True

def validate_amount(amount: Union[float, Decimal]) -> bool:
    """
    Validate a monetary amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If amount is invalid
    """
    with tracer.start_as_current_span("validate_amount") as span:
        span.set_attribute("amount", str(amount))
        
        if not isinstance(amount, (float, Decimal)):
            raise ValidationError("Amount must be a number", ["amount"])
            
        if amount <= 0:
            raise ValidationError("Amount must be positive", ["amount"])
            
        return True

def validate_date(date_str: str, format: str = "%Y-%m-%d") -> datetime:
    """
    Validate and parse a date string.
    
    Args:
        date_str: Date string to validate
        format: Date format string
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValidationError: If date is invalid
    """
    with tracer.start_as_current_span("validate_date") as span:
        span.set_attribute("date_str", date_str)
        span.set_attribute("format", format)
        
        try:
            return datetime.strptime(date_str, format)
        except ValueError:
            raise ValidationError(f"Invalid date format. Expected: {format}", ["date"])

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present in the data.
    
    Args:
        data: Dictionary containing the data
        required_fields: List of required field names
        
    Raises:
        ValidationError: If any required field is missing
    """
    with tracer.start_as_current_span("validate_required_fields") as span:
        span.set_attribute("required_fields", required_fields)
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                missing_fields
            )

def validate_dict_schema(data: Dict[str, Any], schema: Dict[str, type]) -> None:
    """
    Validate that a dictionary matches a given schema.
    
    Args:
        data: Dictionary to validate
        schema: Dictionary defining the expected types
        
    Raises:
        ValidationError: If data doesn't match the schema
    """
    with tracer.start_as_current_span("validate_dict_schema") as span:
        span.set_attribute("schema", str(schema))
        
        for field, expected_type in schema.items():
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", [field])
                
            if not isinstance(data[field], expected_type):
                raise ValidationError(
                    f"Invalid type for field '{field}'. Expected: {expected_type.__name__}",
                    [field]
                )

def validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
    """
    Validate the length of a string value.
    
    Args:
        value: String value to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length (optional)
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If length is invalid
    """
    with tracer.start_as_current_span("validate_length") as span:
        span.set_attribute("min_length", min_length)
        span.set_attribute("max_length", max_length)
        
        length = len(value)
        if length < min_length:
            raise ValidationError(
                f"Value must be at least {min_length} characters long",
                ["length"]
            )
            
        if max_length is not None and length > max_length:
            raise ValidationError(
                f"Value must be at most {max_length} characters long",
                ["length"]
            )
            
        return True
