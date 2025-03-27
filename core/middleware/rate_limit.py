"""
Rate limiting middleware for FinancialMediator.

This module provides rate limiting functionality using Redis as the storage backend.
It includes both a global middleware and a decorator for view-specific rate limiting.

The rate limiting system:
1. Uses Redis for distributed rate limiting
2. Supports both global and view-specific rate limits
3. Provides detailed error responses when limits are exceeded
4. Supports custom rate limits per view

Environment Variables:
- RATE_LIMIT_REQUESTS_PER_MINUTE: Default requests per minute (default: 100)
- RATE_LIMIT_WINDOW_SECONDS: Default window duration in seconds (default: 60)
"""

from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time
import os
from typing import Callable, Optional
from functools import wraps

class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to implement rate limiting using Redis.
    
    This middleware:
    1. Tracks requests per minute per IP address
    2. Uses Redis for distributed rate limiting
    3. Provides detailed error responses when limits are exceeded
    
    Configuration:
    - RATE_LIMIT_REQUESTS_PER_MINUTE: Number of requests allowed per minute
    - RATE_LIMIT_WINDOW_SECONDS: Duration of the rate limiting window in seconds
    """
    
    def __init__(self, get_response: Callable):
        """
        Initialize the rate limit middleware.
        
        Args:
            get_response: Callable to get the response
        """
        self.get_response = get_response
        self.rate_limit = int(os.getenv('RATE_LIMIT_REQUESTS_PER_MINUTE', 100))
        self.window = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', 60))
        self.cache_key_prefix = 'rate_limit_'
        
    def process_request(self, request):
        """
        Process incoming request and apply rate limiting.
        
        Args:
            request: Django request object
            
        Returns:
            JsonResponse: Error response if rate limit is exceeded, None otherwise
        """
        client_ip = self.get_client_ip(request)
        if not client_ip:
            return JsonResponse(
                {'error': 'IP address not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cache_key = f'{self.cache_key_prefix}{client_ip}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.rate_limit:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'limit': self.rate_limit,
                    'window': self.window
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
            
        cache.incr(cache_key, 1)
        cache.expire(cache_key, self.window)
        
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        
        Args:
            request: Django request object
            
        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

def rate_limit(
    requests_per_minute: int = 100,
    window_seconds: int = 60,
    key: Optional[str] = None
) -> Callable:
    """
    Decorator to apply rate limiting to a view function.
    
    Args:
        requests_per_minute: Number of requests allowed per minute
        window_seconds: Duration of the rate limiting window in seconds
        key: Optional key to use for rate limiting (default: view function name)
        
    Returns:
        Callable: Decorated view function
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            client_ip = RateLimitMiddleware.get_client_ip(request)
            if not client_ip:
                return JsonResponse(
                    {'error': 'IP address not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            cache_key = f'rate_limit_{key or view_func.__name__}_{client_ip}'
            current_count = cache.get(cache_key, 0)
            
            if current_count >= requests_per_minute:
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'limit': requests_per_minute,
                        'window': window_seconds
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
                
            cache.incr(cache_key, 1)
            cache.expire(cache_key, window_seconds)
            return view_func(request, *args, **kwargs)
            
        return _wrapped_view
    return decorator

class RateLimitException(Exception):
    """
    Exception raised when rate limit is exceeded.
    
    Attributes:
        message: Error message
        limit: Number of requests allowed
        window: Duration of the rate limiting window
    """
    def __init__(self, message: str, limit: int, window: int):
        super().__init__(message)
        self.limit = limit
        self.window = window

class RateLimitConfig:
    """
    Configuration class for rate limiting.
    
    This class provides a convenient way to configure rate limiting for views.
    
    Example usage:
    ```python
    @rate_limit_config(
        requests_per_minute=100,
        window_seconds=60,
        key='custom_key'
    )
    def my_view(request):
        pass
    ```
    """
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        window_seconds: int = 60,
        key: Optional[str] = None
    ):
        """
        Initialize rate limit configuration.
        
        Args:
            requests_per_minute: Number of requests allowed per minute
            window_seconds: Duration of the rate limiting window in seconds
            key: Optional key to use for rate limiting
        """
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.key = key
        
    def __call__(self, view_func: Callable) -> Callable:
        return rate_limit(
            requests_per_minute=self.requests_per_minute,
            window_seconds=self.window_seconds,
            key=self.key
        )(view_func)
