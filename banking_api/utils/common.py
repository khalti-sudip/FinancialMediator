"""
Common utility functions for the banking_api application.

This module contains utility functions that are used across multiple modules.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import json
from django.db import transaction
from django.http import HttpRequest
from banking_api.exceptions import FinancialMediatorError

def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: The Django HttpRequest object
        
    Returns:
        The client's IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request: HttpRequest) -> Optional[str]:
    """
    Get the user agent from the request.
    
    Args:
        request: The Django HttpRequest object
        
    Returns:
        The user agent string or None if not present
    """
    return request.META.get('HTTP_USER_AGENT')

def format_timestamp(timestamp: datetime) -> str:
    """
    Format a datetime object to a consistent string format.
    
    Args:
        timestamp: The datetime object to format
        
    Returns:
        Formatted timestamp string
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def validate_request_data(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that all required fields are present in request data.
    
    Args:
        data: The request data dictionary
        required_fields: List of required field names
        
    Raises:
        FinancialMediatorError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise FinancialMediatorError(
            f"Missing required fields: {', '.join(missing_fields)}",
            code="INVALID_REQUEST"
        )

def safe_json_loads(data: str) -> Dict[str, Any]:
    """
    Safely load JSON data with error handling.
    
    Args:
        data: The JSON string to parse
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FinancialMediatorError: If JSON parsing fails
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise FinancialMediatorError(
            f"Invalid JSON: {str(e)}",
            code="INVALID_JSON"
        )

def create_audit_log_details(
    action: str,
    resource_id: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a standardized audit log details dictionary.
    
    Args:
        action: The action being performed
        resource_id: The ID of the resource
        details: Additional details about the action
        
    Returns:
        Standardized audit log details dictionary
    """
    return {
        "action": action,
        "resource_id": resource_id,
        "details": details,
        "timestamp": format_timestamp(datetime.now())
    }
