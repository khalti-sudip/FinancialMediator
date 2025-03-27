"""Utility functions for provider management."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Provider, ProviderKey, ProviderWebhook
from banking_api.exceptions import ProviderError
from banking_api.utils.common import get_client_ip, get_user_agent

def validate_provider_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate provider data before creation or update.
    
    Args:
        data: Dictionary containing provider data
        
    Returns:
        Validated data dictionary
        
    Raises:
        ProviderError: If validation fails
    """
    required_fields = ["name", "type", "status"]
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise ProviderError(
            f"Missing required fields: {', '.join(missing_fields)}",
            code="INVALID_REQUEST"
        )
    
    # Validate name
    if not isinstance(data["name"], str) or not data["name"].strip():
        raise ProviderError("Name must be a non-empty string", code="INVALID_NAME")
    
    # Validate type
    valid_types = ["bank", "payment_gateway", "financial_institution"]
    if data["type"] not in valid_types:
        raise ProviderError(
            f"Invalid provider type. Must be one of: {', '.join(valid_types)}",
            code="INVALID_TYPE"
        )
    
    # Validate status
    valid_statuses = ["active", "inactive", "pending", "suspended"]
    if data["status"] not in valid_statuses:
        raise ProviderError(
            f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            code="INVALID_STATUS"
        )
    
    return data

def generate_provider_key(provider_id: int, key_type: str = "api") -> str:
    """
    Generate a unique provider key.
    
    Args:
        provider_id: ID of the provider
        key_type: Type of key to generate (api, web, etc.)
        
    Returns:
        Generated key string
    """
    prefix = {
        "api": "api_key_",
        "web": "web_key_",
        "admin": "admin_key_"
    }.get(key_type, "key_")
    
    return f"{prefix}{provider_id}_{uuid.uuid4().hex[:12]}"

def validate_provider_key(key: str) -> bool:
    """
    Validate a provider key format.
    
    Args:
        key: The key string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(key, str):
        return False
    
    # Basic format validation
    if not key.startswith(("api_key_", "web_key_", "admin_key_")):
        return False
    
    # Check length
    if len(key) < 20:  # Minimum length
        return False
    
    return True

def get_provider_by_key(key: str) -> Optional[Provider]:
    """
    Get a provider by its key.
    
    Args:
        key: The provider key to look up
        
    Returns:
        Provider instance if found, None otherwise
    """
    try:
        key_obj = ProviderKey.objects.get(key_value=key)
        return key_obj.provider
    except ProviderKey.DoesNotExist:
        return None

def validate_webhook_url(url: str) -> bool:
    """
    Validate a webhook URL format.
    
    Args:
        url: The URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(url, str):
        return False
    
    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        return False
    
    # Check for common webhook endpoints
    valid_endpoints = [
        "/webhook",
        "/callback",
        "/notification",
        "/event"
    ]
    
    if not any(endpoint in url.lower() for endpoint in valid_endpoints):
        return False
    
    return True

def format_webhook_response(
    status: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format a standardized webhook response.
    
    Args:
        status: The response status (success, error, etc.)
        message: The response message
        data: Optional data to include in the response
        
    Returns:
        Formatted response dictionary
    """
    response = {
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def process_webhook_event(
    webhook_id: int,
    event_type: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process a webhook event.
    
    Args:
        webhook_id: ID of the webhook configuration
        event_type: Type of event being processed
        payload: Event payload data
        
    Returns:
        Processed response dictionary
        
    Raises:
        ProviderError: If webhook processing fails
    """
    try:
        webhook = ProviderWebhook.objects.get(id=webhook_id)
        
        # Validate event type
        if event_type not in webhook.supported_events:
            raise ProviderError(
                f"Unsupported event type: {event_type}",
                code="INVALID_EVENT"
            )
        
        # Process event based on type
        response = {
            "success": True,
            "event_type": event_type,
            "provider": webhook.provider.name,
            "processed_at": datetime.now().isoformat()
        }
        
        # Add payload data if needed
        if webhook.include_payload:
            response["payload"] = payload
        
        return response
    except ProviderWebhook.DoesNotExist:
        raise ProviderError(
            "Webhook configuration not found",
            code="WEBHOOK_NOT_FOUND"
        )
    except Exception as e:
        raise ProviderError(
            f"Error processing webhook: {str(e)}",
            code="WEBHOOK_PROCESSING_ERROR"
        )

def get_provider_status(provider_id: int) -> Dict[str, Any]:
    """
    Get the current status of a provider.
    
    Args:
        provider_id: ID of the provider
        
    Returns:
        Dictionary containing provider status information
        
    Raises:
        ProviderError: If provider not found
    """
    try:
        provider = Provider.objects.get(id=provider_id)
        
        status_info = {
            "id": provider.id,
            "name": provider.name,
            "status": provider.status,
            "type": provider.type,
            "last_updated": provider.updated_at.isoformat(),
            "key_count": provider.providerkey_set.count(),
            "webhook_count": provider.providerwebhook_set.count(),
            "is_active": provider.is_active
        }
        
        return status_info
    except Provider.DoesNotExist:
        raise ProviderError(
            "Provider not found",
            code="PROVIDER_NOT_FOUND"
        )

def log_provider_action(
    provider_id: int,
    action: str,
    details: Dict[str, Any],
    request
) -> None:
    """
    Log a provider-related action.
    
    Args:
        provider_id: ID of the provider
        action: The action being performed
        details: Additional details about the action
        request: The HTTP request object
    """
    from banking_api.services.audit_log_service import AuditLogService
    
    audit_log_service = AuditLogService()
    
    audit_log_service.create_audit_log(
        user_id=request.user.id,
        action=f"PROVIDER_{action.upper()}",
        details={
            "provider_id": str(provider_id),
            "action": action,
            **details
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request)
    )

def get_provider_statistics() -> Dict[str, Any]:
    """
    Get statistics about providers.
    
    Returns:
        Dictionary containing provider statistics
    """
    stats = {
        "total_providers": Provider.objects.count(),
        "active_providers": Provider.objects.filter(status="active").count(),
        "provider_types": {},
        "status_distribution": {}
    }
    
    # Get provider type distribution
    for provider_type in Provider.objects.values_list("type", flat=True).distinct():
        stats["provider_types"][provider_type] = Provider.objects.filter(type=provider_type).count()
    
    # Get status distribution
    for status in Provider.objects.values_list("status", flat=True).distinct():
        stats["status_distribution"][status] = Provider.objects.filter(status=status).count()
    
    return stats
