"""Rate limiting middleware for API endpoints."""

from functools import wraps
from typing import Callable, Any, Optional
import time
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message="Rate limit exceeded", wait_time=None):
        self.message = message
        self.wait_time = wait_time
        super().__init__(self.message)


def get_client_ip(request):
    """Get the client's IP address from the request.
    
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


def rate_limit(requests=100, duration=60, key_prefix='rl'):
    """
    Decorator to apply rate limiting to a view.
    
    Args:
        requests: Maximum number of requests allowed in the duration
        duration: Time window in seconds
        key_prefix: Prefix for cache keys
    
    Returns:
        Decorated function with rate limiting
    
    Example:
        @api_view(['GET'])
        @rate_limit(requests=100, duration=60)
        def get_resource(request):
            return Response({'data': 'resource'})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            # Generate a unique key for this client
            user_id = request.user.id if request.user.is_authenticated else None
            ip = get_client_ip(request)
            key = f"{key_prefix}:{ip}:{user_id or 'anonymous'}"
            
            # Get current count and timestamp
            now = int(time.time())
            window_start = now - duration
            
            # Using cache for rate limiting
            request_history = cache.get(key) or []
            
            # Filter out old requests
            request_history = [t for t in request_history if t > window_start]
            
            # Check if rate limit is exceeded
            if len(request_history) >= requests:
                oldest_request = min(request_history) if request_history else now
                wait_time = oldest_request - window_start
                response = {
                    "error": "Rate limit exceeded",
                    "wait_seconds": wait_time,
                    "limit": requests,
                    "duration": duration
                }
                
                # Add rate limit headers
                headers = {
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(oldest_request + duration),
                    "Retry-After": str(wait_time)
                }
                
                return JsonResponse(response, status=status.HTTP_429_TOO_MANY_REQUESTS, headers=headers)
            
            # Add current timestamp to history and store
            request_history.append(now)
            cache.set(key, request_history, duration * 2)  # Store for twice the duration to handle edge cases
            
            # Add rate limit headers to the response
            response = view_func(self, request, *args, **kwargs)
            response["X-RateLimit-Limit"] = str(requests)
            response["X-RateLimit-Remaining"] = str(requests - len(request_history))
            response["X-RateLimit-Reset"] = str(now + duration)
            
            return response
        
        return wrapped_view
    
    # Handle both @rate_limit and @rate_limit()
    if callable(requests):
        view_func = requests
        requests = 100
        return decorator(view_func)
    
    return decorator


class RateLimitMiddleware:
    """Middleware for applying rate limiting to all requests."""
    
    def __init__(self, get_response):
        """Initialize middleware.
        
        Args:
            get_response: Django response getter
        """
        self.get_response = get_response
        self.requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.duration = getattr(settings, 'RATE_LIMIT_DURATION', 60)
    
    def __call__(self, request):
        """Process the request.
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: The response
        """
        # Skip rate limiting for certain paths
        if any(path in request.path for path in ['/admin/', '/static/', '/media/']):
            return self.get_response(request)
        
        # Generate a unique key for this client
        user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None
        ip = get_client_ip(request)
        key = f"global_rl:{ip}:{user_id or 'anonymous'}"
        
        # Check rate limiting
        now = int(time.time())
        window_start = now - self.duration
        
        request_history = cache.get(key) or []
        request_history = [t for t in request_history if t > window_start]
        
        if len(request_history) >= self.requests:
            oldest_request = min(request_history) if request_history else now
            wait_time = oldest_request - window_start
            response = JsonResponse({
                "error": "Global rate limit exceeded",
                "wait_seconds": wait_time,
                "limit": self.requests,
                "duration": self.duration
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            response["X-RateLimit-Limit"] = str(self.requests)
            response["X-RateLimit-Remaining"] = "0"
            response["X-RateLimit-Reset"] = str(oldest_request + self.duration)
            response["Retry-After"] = str(wait_time)
            
            return response
        
        # Add current timestamp to history and store
        request_history.append(now)
        cache.set(key, request_history, self.duration * 2)
        
        # Get the response
        response = self.get_response(request)
        
        # Add headers
        response["X-RateLimit-Limit"] = str(self.requests)
        response["X-RateLimit-Remaining"] = str(self.requests - len(request_history))
        response["X-RateLimit-Reset"] = str(now + self.duration)
        
        return response
