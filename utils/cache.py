"""
Caching utilities for FinancialMediator.
"""

from typing import Any, Callable, Optional
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import hashlib
import json


def cache_result(
    timeout: int = 300,  # 5 minutes default
    key_prefix: str = "cache",
    use_args: bool = True,
    use_kwargs: bool = True
) -> Callable:
    """
    Decorator to cache function results using Redis.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
        use_args: Whether to include function arguments in cache key
        use_kwargs: Whether to include keyword arguments in cache key
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key
            key_parts = [key_prefix, func.__name__]
            
            if use_args:
                key_parts.append(str(args))
            
            if use_kwargs:
                key_parts.append(str(kwargs))
            
            key = hashlib.md5("".join(key_parts).encode()).hexdigest()
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return json.loads(result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, json.dumps(result), timeout)
            
            return result
        
        return wrapper


def cache_provider_status(provider_id: str, timeout: int = 300) -> Callable:
    """
    Decorator to cache provider status checks.
    
    Args:
        provider_id: ID of the provider
        timeout: Cache timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"provider_status:{provider_id}"
            result = cache.get(key)
            
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            return result
        
        return wrapper


def cache_request_data(
    request_id: str,
    timeout: int = 3600  # 1 hour default
) -> Callable:
    """
    Decorator to cache request data.
    
    Args:
        request_id: ID of the request
        timeout: Cache timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"request_data:{request_id}"
            result = cache.get(key)
            
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            return result
        
        return wrapper


def get_cached_value(key: str, default: Optional[Any] = None) -> Any:
    """
    Get a value from cache with fallback to default.
    
    Args:
        key: Cache key
        default: Default value if key not found
        
    Returns:
        Cached value or default
    """
    return cache.get(key, default)


def set_cached_value(key: str, value: Any, timeout: int = 300) -> None:
    """
    Set a value in cache with timeout.
    
    Args:
        key: Cache key
        value: Value to cache
        timeout: Cache timeout in seconds
    """
    cache.set(key, value, timeout)


def invalidate_cache(key: str) -> None:
    """
    Invalidate a cache entry.
    
    Args:
        key: Cache key to invalidate
    """
    cache.delete(key)


def invalidate_provider_cache(provider_id: str) -> None:
    """
    Invalidate all cache entries for a provider.
    
    Args:
        provider_id: ID of the provider
    """
    cache.delete_pattern(f"provider_*:{provider_id}")
