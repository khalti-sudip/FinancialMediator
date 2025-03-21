import hmac
import hashlib
import base64
import json
import time
import logging
from functools import wraps
from flask import request, jsonify

# Configure logging
logger = logging.getLogger(__name__)


def sign_request(data, secret_key):
    """
    Sign request data using HMAC-SHA256
    
    Args:
        data (str): The data to sign (typically JSON stringified)
        secret_key (str): The secret key for signing
    
    Returns:
        str: Base64-encoded signature
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, dict):
        data = json.dumps(data).encode('utf-8')
    
    if isinstance(secret_key, str):
        secret_key = secret_key.encode('utf-8')
    
    signature = hmac.new(secret_key, data, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')


def verify_request_signature(data, signature, secret_key=None):
    """
    Verify the signature of request data
    
    Args:
        data (bytes or str): The data that was signed
        signature (str): The signature to verify
        secret_key (str, optional): The secret key for verification
    
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if secret_key is None:
        # In real implementation, this would retrieve the correct secret key
        # based on the request details (e.g., API key, client ID)
        logger.warning("No secret key provided for signature verification")
        return False
    
    expected_signature = sign_request(data, secret_key)
    return hmac.compare_digest(signature, expected_signature)


def verify_request(requires_signature=True):
    """
    Decorator to verify request authenticity
    
    Args:
        requires_signature (bool): Whether the request requires a signature
    
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if requires_signature:
                signature = request.headers.get('X-Signature')
                if not signature:
                    logger.warning("Missing signature in request")
                    return jsonify({'error': 'Missing signature'}), 401
                
                # Get the API key or client ID to determine the correct secret
                api_key = request.headers.get('X-API-Key')
                if not api_key:
                    logger.warning("Missing API key in request")
                    return jsonify({'error': 'Missing API key'}), 401
                
                # In a real implementation, retrieve the secret for this API key
                # For now, use a placeholder
                secret_key = "placeholder_secret"
                
                # Verify the signature
                request_data = request.get_data()
                if not verify_request_signature(request_data, signature, secret_key):
                    logger.warning("Invalid signature in request")
                    return jsonify({'error': 'Invalid signature'}), 401
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def generate_nonce():
    """
    Generate a unique nonce for request signing
    
    Returns:
        str: A unique nonce
    """
    return hashlib.sha256(str(time.time()).encode()).hexdigest()


def encrypt_sensitive_data(data, encryption_key):
    """
    Encrypt sensitive data
    
    Args:
        data (str): The data to encrypt
        encryption_key (str): The encryption key
    
    Returns:
        str: Encrypted data
    """
    # This is a placeholder. In a real implementation, use a secure encryption library
    logger.warning("Using placeholder encryption - not secure for production")
    return f"ENCRYPTED:{data}"


def decrypt_sensitive_data(encrypted_data, encryption_key):
    """
    Decrypt sensitive data
    
    Args:
        encrypted_data (str): The data to decrypt
        encryption_key (str): The encryption key
    
    Returns:
        str: Decrypted data
    """
    # This is a placeholder. In a real implementation, use a secure encryption library
    logger.warning("Using placeholder decryption - not secure for production")
    if encrypted_data.startswith("ENCRYPTED:"):
        return encrypted_data[10:]
    return encrypted_data
