import json
import logging
import datetime
import threading

from django.http import HttpRequest

# Thread local storage to store request information
local = threading.local()

def get_current_request():
    """Get the current request from thread local storage"""
    if hasattr(local, 'request'):
        return local.request
    return None

def set_current_request(request):
    """Set the current request in thread local storage"""
    local.request = request

class RequestInfoFilter(logging.Filter):
    """
    Filter to add request-specific information to log records.
    Safely handles both request and non-request contexts.
    """
    def filter(self, record):
        # Default values
        record.request_id = "no_request_id"
        record.remote_addr = "no_remote_addr"
        record.url = "no_url"
        record.method = "no_method"
        record.user_id = "no_user_id"
        
        # Try to get request info from thread local storage
        request = get_current_request()
        
        if request and isinstance(request, HttpRequest):
            # Add request ID if available
            if hasattr(request, 'request_id'):
                record.request_id = request.request_id
            
            # Add remote address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                record.remote_addr = x_forwarded_for.split(',')[0].strip()
            else:
                record.remote_addr = request.META.get('REMOTE_ADDR', 'unknown')
            
            # Add URL and method
            record.url = request.path
            record.method = request.method
            
            # Add user ID if user is authenticated
            if hasattr(request, 'user') and request.user.is_authenticated:
                record.user_id = str(request.user.id)
        
        return True


class JSONFormatter(logging.Formatter):
    """
    Formatter for structured JSON logs.
    """
    def format(self, record):
        log_data = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'filename': record.filename,
            'lineno': record.lineno,
        }
        
        # Add request-specific fields if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'remote_addr'):
            log_data['remote_addr'] = record.remote_addr
        if hasattr(record, 'url'):
            log_data['url'] = record.url
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        # Add exception info if available
        if record.exc_info:
            log_data['exc_info'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)