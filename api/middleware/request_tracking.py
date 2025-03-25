"""
Request Tracking Middleware.

This module provides middleware for tracking and logging API requests.
It includes:
- Request timing
- Response status tracking
- User identification
- Request/Response logging
- Performance monitoring
"""

import time
import logging
from functools import wraps
from django.utils import timezone
from django.core.cache import cache
from api.models import RequestLog

logger = logging.getLogger(__name__)

def track_request(view_func):
    """
    Decorator to track API request details.
    
    This decorator:
    1. Logs request details
    2. Measures response time
    3. Records response status
    4. Updates request statistics
    
    Args:
        view_func: The view function to wrap
        
    Returns:
        function: Wrapped view function
    """
    @wraps(view_func)
    def wrapper(view_instance, request, *args, **kwargs):
        # Start timing
        start_time = time.time()
        
        try:
            # Execute view
            response = view_func(view_instance, request, *args, **kwargs)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Log request details
            log_request(
                request=request,
                response=response,
                response_time=response_time,
                view_name=view_func.__name__,
            )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "view": view_func.__name__,
                    "error": str(e),
                    "user": request.user.id if request.user.is_authenticated else None,
                },
                exc_info=True,
            )
            raise
            
    return wrapper

class RequestTrackingMiddleware:
    """Middleware for tracking all incoming requests."""
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view
        """
        self.get_response = get_response
        
    def __call__(self, request):
        """
        Process the request.
        
        Args:
            request: The incoming request
            
        Returns:
            HttpResponse: The response
        """
        # Start timing
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Log request if it's an API request
        if request.path.startswith("/api/"):
            log_request(
                request=request,
                response=response,
                response_time=response_time,
            )
            
        return response

def log_request(request, response, response_time, view_name=None):
    """
    Log request details to database and update statistics.
    
    Args:
        request: The HTTP request
        response: The HTTP response
        response_time: Time taken to process the request
        view_name: Optional name of the view that handled the request
    """
    try:
        # Create request log entry
        RequestLog.objects.create(
            path=request.path,
            method=request.method,
            view_name=view_name,
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            response_code=response.status_code,
            response_time=response_time,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        
        # Update request statistics in cache
        update_request_stats(response_time, response.status_code)
        
    except Exception as e:
        logger.error("Failed to log request", exc_info=True)

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    
    Args:
        request: The HTTP request
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def update_request_stats(response_time, status_code):
    """
    Update request statistics in cache.
    
    Args:
        response_time: Time taken to process the request
        status_code: HTTP status code of the response
    """
    try:
        # Get current hour's key
        current_hour = timezone.now().strftime("%Y%m%d%H")
        stats_key = f"request_stats:{current_hour}"
        
        # Get or initialize stats
        stats = cache.get(stats_key) or {
            "count": 0,
            "total_time": 0,
            "error_count": 0,
        }
        
        # Update stats
        stats["count"] += 1
        stats["total_time"] += response_time
        if status_code >= 400:
            stats["error_count"] += 1
            
        # Store updated stats
        cache.set(stats_key, stats, timeout=3600)  # 1 hour
        
    except Exception as e:
        logger.error("Failed to update request stats", exc_info=True)
