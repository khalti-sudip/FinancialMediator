
from django.core.cache import cache
from rest_framework.exceptions import Throttled
from django.conf import settings

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = getattr(settings, 'API_RATE_LIMIT', 100)
        self.rate_period = getattr(settings, 'API_RATE_PERIOD', 3600)

    def __call__(self, request):
        if request.path.startswith('/api/'):
            client_ip = request.META.get('REMOTE_ADDR')
            cache_key = f'rate_limit:{client_ip}'
            
            request_count = cache.get(cache_key, 0)
            if request_count >= self.rate_limit:
                raise Throttled()
            
            cache.set(cache_key, request_count + 1, self.rate_period)
        
        return self.get_response(request)
from django.core.cache import cache
from rest_framework.throttling import SimpleRateThrottle

class CustomRateThrottle(SimpleRateThrottle):
    rate = '100/minute'  # Adjust as needed
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return f"throttle_{ident}"
