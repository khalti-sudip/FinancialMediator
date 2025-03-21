import uuid
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('banking_api')

class RequestIdMiddleware(MiddlewareMixin):
    """
    Middleware to assign a unique ID to each request for tracking.
    This ID is attached to the request object and can be accessed throughout the request.
    """
    
    def process_request(self, request):
        """Process the request and attach a unique ID"""
        # Get request ID from header if provided or generate a new one
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id
        
        # Store request ID in current thread's local storage for logging
        return None
    
    def process_response(self, request, response):
        """Add request ID to response headers"""
        # Only add header if request_id was set
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        return response