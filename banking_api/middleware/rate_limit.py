from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseTooManyRequests
import time

class RateLimitMiddleware:
    """
    Rate limiting middleware using Redis for distributed rate limiting.
    
    Implements sliding window algorithm for more accurate rate limiting.
    
    Key Features:
    - Distributed rate limiting using Redis
    - Sliding window algorithm for accurate rate limiting
    - Configurable rate limits per endpoint
    - IP-based rate limiting
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: Callable to get the response
        """
        self.get_response = get_response
        self.requests_per_second = getattr(settings, "RATE_LIMIT_REQUESTS", 100)
        self.window_size = getattr(settings, "RATE_LIMIT_DURATION", 1)  # 1 second window
        self.bucket_size = getattr(settings, "RATE_LIMIT_BUCKET_SIZE", 1000)
        self.cache_prefix = "rate_limit"
    
    def __call__(self, request):
        """
        Process the request and enforce rate limits.
        
        Args:
            request: HTTP request object
            
        Returns:
            HTTP response
            
        Raises:
            HttpResponseTooManyRequests: If rate limit is exceeded
        """
        if request.path.startswith("/api/"):
            client_ip = request.META.get("REMOTE_ADDR")
            
            # Get current timestamp
            current_time = int(time.time())
            
            # Generate cache keys for current and previous windows
            current_window_key = f"rate_limit:{client_ip}:{current_time}"
            previous_window_key = f"rate_limit:{client_ip}:{current_time - self.window_size}"
            
            # Get request counts from both windows
            current_count = cache.get(current_window_key, 0)
            previous_count = cache.get(previous_window_key, 0)
            
            # Calculate total requests in the sliding window
            total_requests = current_count + previous_count
            
            # Check if rate limit is exceeded
            if total_requests >= self.requests_per_second:
                reset_time = cache.ttl(current_window_key) or self.window_size
                headers = {
                    "X-RateLimit-Limit": str(self.requests_per_second),
                    "X-RateLimit-Remaining": str(self.requests_per_second - total_requests),
                    "X-RateLimit-Reset": str(int(time.time()) + reset_time)
                }
                return HttpResponseTooManyRequests(
                    "Rate limit exceeded. Please try again later.",
                    headers=headers
                )
            
            # Increment current window count
            cache.incr(current_window_key, 1)
            
            # Set expiration for current window
            cache.expire(current_window_key, self.window_size)
            
            # Clean up old windows
            cache.delete(previous_window_key)

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view to enforce per-view rate limits.
        
        Args:
            request: HTTP request object
            view_func: View function
            view_args: View arguments
            view_kwargs: View keyword arguments
            
        Returns:
            None or HTTP response if rate limit is exceeded
        """
        if hasattr(view_func, "rate_limit"):
            view_rate_limit = view_func.rate_limit
            client_ip = request.META.get("REMOTE_ADDR")
            
            # Generate cache key for this view
            view_key = f"rate_limit:view:{client_ip}:{view_func.__name__}"
            
            # Get current count
            current_count = cache.get(view_key, 0)
            
            if current_count >= view_rate_limit:
                reset_time = cache.ttl(view_key) or self.window_size
                headers = {
                    "X-RateLimit-Limit": str(view_rate_limit),
                    "X-RateLimit-Remaining": str(view_rate_limit - current_count),
                    "X-RateLimit-Reset": str(int(time.time()) + reset_time)
                }
                return HttpResponseTooManyRequests(
                    "Rate limit exceeded for this endpoint. Please try again later.",
                    headers=headers
                )
            
            # Increment count and set expiration
            cache.incr(view_key, 1)
            cache.expire(view_key, self.window_size)

# Decorator for per-view rate limiting
def view_rate_limit(limit):
    """
    Decorator to apply rate limiting to a view.
    
    Args:
        limit: Maximum number of requests allowed per window
    """
    def decorator(view_func):
        view_func.rate_limit = limit
        return view_func
    return decorator
