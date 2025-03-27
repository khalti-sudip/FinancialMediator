from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time
from typing import Callable, Optional
from functools import wraps

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware to implement rate limiting using Redis."""
    
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds
        self.cache_key_prefix = 'rate_limit_'
        
    def process_request(self, request):
        """Process incoming request and apply rate limiting."""
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
        """Get client IP address from request."""
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
    """Decorator to apply rate limiting to a view function."""
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
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str, limit: int, window: int):
        super().__init__(message)
        self.limit = limit
        self.window = window

class RateLimitConfig:
    """Configuration class for rate limiting."""
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        window_seconds: int = 60,
        key: Optional[str] = None
    ):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self.key = key
        
    def __call__(self, view_func: Callable) -> Callable:
        return rate_limit(
            requests_per_minute=self.requests_per_minute,
            window_seconds=self.window_seconds,
            key=self.key
        )(view_func)
