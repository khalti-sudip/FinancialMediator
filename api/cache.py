import logging
import json
import hashlib
from datetime import datetime, timedelta
from flask import current_app

# Define a simple in-memory cache
# In production, this would typically be replaced with Redis or similar
CACHE = {}
CACHE_EXPIRY = {}  # Store expiry times

# Configure logging
logger = logging.getLogger(__name__)


def cache_key(data):
    """
    Generate a cache key from request data
    
    Args:
        data (dict): The request data to generate a key for
    
    Returns:
        str: A hash-based cache key
    """
    # Create a deterministic representation of the data
    # Exclude non-cacheable or changing fields like timestamps and request IDs
    cache_data = {
        'transaction_type': data.get('transaction_type'),
        'source_system': data.get('source_system'),
        'target_system': data.get('target_system'),
        'payload': data.get('payload')
    }
    
    # Add user-specific information if present
    if 'user_id' in data:
        cache_data['user_id'] = data['user_id']
    
    # For financial transactions, include amount and currency
    if data.get('transaction_type') in ['payment', 'transfer', 'withdrawal', 'deposit']:
        cache_data['amount'] = data.get('amount')
        cache_data['currency'] = data.get('currency')
    
    # Create a string representation and hash it
    data_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


def cache_response(request_data, response_data, ttl=300):
    """
    Cache a response for a given request
    
    Args:
        request_data (dict): The original request data
        response_data (dict): The response data to cache
        ttl (int): Time to live in seconds (default: 5 minutes)
    """
    try:
        # Skip caching for non-cacheable transaction types
        if not request_data.get('cacheable', False):
            return
        
        transaction_type = request_data.get('transaction_type', '')
        
        # Some transaction types should never be cached
        non_cacheable_types = ['payment', 'transfer', 'withdrawal', 'deposit']
        if transaction_type in non_cacheable_types:
            logger.debug(f"Skipping cache for non-cacheable transaction type: {transaction_type}")
            return
        
        key = cache_key(request_data)
        CACHE[key] = response_data
        CACHE_EXPIRY[key] = datetime.utcnow() + timedelta(seconds=ttl)
        
        logger.debug(f"Cached response for key {key} with TTL of {ttl} seconds")
    except Exception as e:
        logger.error(f"Error caching response: {str(e)}")


def get_cached_response(request_data):
    """
    Get a cached response for a request if available
    
    Args:
        request_data (dict): The request data to get a cached response for
    
    Returns:
        dict or None: The cached response or None if not found or expired
    """
    try:
        # Skip cache for non-cacheable transaction types
        if not request_data.get('cacheable', False):
            return None
        
        key = cache_key(request_data)
        
        # Check if we have this key in the cache
        if key not in CACHE:
            return None
        
        # Check if the cached response has expired
        if CACHE_EXPIRY[key] < datetime.utcnow():
            logger.debug(f"Cache expired for key {key}")
            del CACHE[key]
            del CACHE_EXPIRY[key]
            return None
        
        logger.debug(f"Cache hit for key {key}")
        return CACHE[key]
    except Exception as e:
        logger.error(f"Error retrieving cached response: {str(e)}")
        return None


def clear_cache():
    """Clear all cached responses"""
    global CACHE, CACHE_EXPIRY
    CACHE = {}
    CACHE_EXPIRY = {}
    logger.debug("Cache cleared")


def clear_expired_cache():
    """Clear only expired cache entries"""
    now = datetime.utcnow()
    expired_keys = [k for k, v in CACHE_EXPIRY.items() if v < now]
    
    for key in expired_keys:
        if key in CACHE:
            del CACHE[key]
        if key in CACHE_EXPIRY:
            del CACHE_EXPIRY[key]
    
    logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
