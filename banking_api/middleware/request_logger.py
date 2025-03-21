import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('banking_api')

class RequestLoggerMiddleware(MiddlewareMixin):
    """
    Middleware to log details about each request including path, method, and timing.
    """
    
    def process_request(self, request):
        """Process the request and record start time"""
        request.start_time = time.time()
        
        # Log the start of the request
        log_data = {
            'request_id': getattr(request, 'request_id', 'unknown'),
            'method': request.method,
            'path': request.path,
            'ip': self._get_client_ip(request),
        }
        
        logger.debug(f"Request started: {request.method} {request.path} [{log_data['request_id']}]")
        return None
    
    def process_response(self, request, response):
        """Process the response and log timing information"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            log_data = {
                'request_id': getattr(request, 'request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'status': response.status_code,
                'duration': f"{duration:.4f}s",
                'ip': self._get_client_ip(request),
            }
            
            logger.debug(
                f"Request completed: {request.method} {request.path} "
                f"[{log_data['request_id']}] - Status: {response.status_code} - "
                f"Duration: {log_data['duration']}"
            )
        
        return response
    
    def _get_client_ip(self, request):
        """Get the client IP address from request headers"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip