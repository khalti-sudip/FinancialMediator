from django.core.cache import cache
from rest_framework.exceptions import Throttled
from django.conf import settings
import time


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests_per_second = getattr(settings, "RATE_LIMIT_REQUESTS", 10000)
        self.window_size = getattr(settings, "RATE_LIMIT_DURATION", 1)  # 1 second window
        self.bucket_size = getattr(settings, "RATE_LIMIT_BUCKET_SIZE", 1000)

    def __call__(self, request):
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
            
            if total_requests >= self.requests_per_second:
                raise Throttled()
            
            # Increment current window count
            cache.incr(current_window_key, 1)
            
            # Set expiration for current window
            cache.expire(current_window_key, self.window_size)
            
            # Clean up old windows
            cache.delete(previous_window_key)

        return self.get_response(request)


from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle


class CustomRateThrottle(SimpleRateThrottle):
    rate = "100/minute"  # Adjust as needed

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return f"throttle_{ident}"
