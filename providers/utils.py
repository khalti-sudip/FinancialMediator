"""
Provider Utilities Module.

This module provides utility functions for:
- Signature verification
- Key generation
- Credential management
- Webhook handling
"""

import hmac
import hashlib
import secrets
import string
import json
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def calculate_signature(data: Dict[str, Any], secret: str) -> str:
    """
    Calculate HMAC signature for webhook data.
    
    Args:
        data: Data to sign
        secret: Secret key for signing
        
    Returns:
        str: Calculated signature
    """
    try:
        # Convert data to string
        data_str = json.dumps(data, sort_keys=True)
        
        # Calculate HMAC
        signature = hmac.new(
            secret.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    except Exception as e:
        logger.error("Failed to calculate signature", exc_info=True)
        raise ValueError(f"Signature calculation failed: {str(e)}")

def verify_signature(data: Dict[str, Any], signature: str, secret: str) -> bool:
    """
    Verify webhook signature.
    
    Args:
        data: Data to verify
        signature: Provided signature
        secret: Secret key for verification
        
    Returns:
        bool: True if signature is valid
    """
    try:
        # Calculate expected signature
        expected = calculate_signature(data, secret)
        
        # Compare signatures
        return hmac.compare_digest(
            signature.encode(),
            expected.encode()
        )
        
    except Exception as e:
        logger.error("Failed to verify signature", exc_info=True)
        return False

def generate_api_key(length: int = 32) -> Dict[str, str]:
    """
    Generate API key pair.
    
    Args:
        length: Key length in bytes
        
    Returns:
        dict: Generated key pair
    """
    try:
        # Generate random strings
        key_id = "".join(
            secrets.choice(string.ascii_letters + string.digits)
            for _ in range(16)
        )
        
        key_secret = secrets.token_hex(length)
        
        return {
            "key_id": key_id,
            "key_secret": key_secret,
        }
        
    except Exception as e:
        logger.error("Failed to generate API key", exc_info=True)
        raise ValueError(f"Key generation failed: {str(e)}")

def generate_provider_credentials(
    provider_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate provider credentials.
    
    Args:
        provider_type: Type of provider
        **kwargs: Additional parameters
        
    Returns:
        dict: Generated credentials
    """
    try:
        # Get generator function
        generator = CREDENTIAL_GENERATORS.get(provider_type)
        if not generator:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        # Generate credentials
        credentials = generator(**kwargs)
        
        # Add metadata
        credentials.update({
            "generated_at": timezone.now().isoformat(),
            "provider_type": provider_type,
        })
        
        return credentials
        
    except Exception as e:
        logger.error(
            f"Failed to generate credentials for {provider_type}",
            exc_info=True
        )
        raise ValueError(f"Credential generation failed: {str(e)}")

def get_webhook_handler(
    provider_type: str,
    event_type: str
) -> Optional[callable]:
    """
    Get webhook event handler.
    
    Args:
        provider_type: Type of provider
        event_type: Type of event
        
    Returns:
        callable: Event handler function
    """
    try:
        # Get handler mapping
        handlers = WEBHOOK_HANDLERS.get(provider_type, {})
        
        # Get specific handler
        handler = handlers.get(event_type)
        if not handler:
            # Try default handler
            handler = handlers.get("default")
        
        return handler
        
    except Exception as e:
        logger.error(
            f"Failed to get handler for {provider_type}.{event_type}",
            exc_info=True
        )
        return None

def get_notification_service():
    """
    Get notification service instance.
    
    Returns:
        NotificationService: Service instance
    """
    try:
        # Import service class
        from core.services import NotificationService
        
        # Get service config
        config = getattr(
            settings,
            "NOTIFICATION_SERVICE",
            {}
        )
        
        # Create instance
        return NotificationService(**config)
        
    except Exception as e:
        logger.error("Failed to get notification service", exc_info=True)
        return None

# Credential generator functions
def generate_payment_credentials(**kwargs) -> Dict[str, str]:
    """Generate payment provider credentials."""
    return {
        "api_key": secrets.token_hex(32),
        "api_secret": secrets.token_hex(32),
        "merchant_id": f"MERCH_{secrets.token_hex(8)}",
    }

def generate_wallet_credentials(**kwargs) -> Dict[str, str]:
    """Generate wallet provider credentials."""
    return {
        "wallet_id": f"WALL_{secrets.token_hex(8)}",
        "access_key": secrets.token_hex(32),
        "secret_key": secrets.token_hex(32),
    }

def generate_bank_credentials(**kwargs) -> Dict[str, str]:
    """Generate bank provider credentials."""
    return {
        "client_id": f"BANK_{secrets.token_hex(8)}",
        "client_secret": secrets.token_hex(32),
        "access_token": secrets.token_hex(32),
    }

def generate_kyc_credentials(**kwargs) -> Dict[str, str]:
    """Generate KYC provider credentials."""
    return {
        "partner_id": f"KYC_{secrets.token_hex(8)}",
        "api_key": secrets.token_hex(32),
        "webhook_secret": secrets.token_hex(32),
    }

# Credential generator mapping
CREDENTIAL_GENERATORS = {
    "payment": generate_payment_credentials,
    "wallet": generate_wallet_credentials,
    "bank": generate_bank_credentials,
    "kyc": generate_kyc_credentials,
}

# Import handlers here to avoid circular imports
from .handlers import (
    payment_handlers,
    wallet_handlers,
    bank_handlers,
    kyc_handlers,
)

# Webhook handler mapping
WEBHOOK_HANDLERS = {
    "payment": payment_handlers,
    "wallet": wallet_handlers,
    "bank": bank_handlers,
    "kyc": kyc_handlers,
}
