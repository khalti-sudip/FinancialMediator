import os
import logging
import logging.handlers
import json
import uuid
from datetime import datetime


class RequestInfoFilter(logging.Filter):
    """
    Filter to add request-specific information to log records.
    Safely handles both request and non-request contexts.
    """
    def filter(self, record):
        try:
            from flask import has_request_context, g, request
            
            if has_request_context():
                # Generate request_id if not present
                if not hasattr(g, 'request_id'):
                    g.request_id = str(uuid.uuid4())
                
                record.request_id = g.request_id
                record.remote_addr = request.remote_addr
                record.url = request.path
                record.method = request.method
            else:
                record.request_id = 'no_request_id'
                record.remote_addr = 'no_remote_addr'
                record.url = 'no_url'
                record.method = 'no_method'
        except Exception:
            # Fallback for when Flask is not available or other errors
            record.request_id = 'logging_error'
            record.remote_addr = 'logging_error'
            record.url = 'logging_error'
            record.method = 'logging_error'
        
        return True


class JSONFormatter(logging.Formatter):
    """
    Formatter for structured JSON logs.
    """
    def format(self, record):
        log_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Mask sensitive data and prevent duplicate handlers
        def mask_sensitive_data(message):
            import re
            return re.sub(r'postgresql://[^@]+@', 'postgresql://****:****@', message)
            
        # Add request info if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'remote_addr'):
            log_record['remote_addr'] = record.remote_addr
        if hasattr(record, 'url'):
            log_record['url'] = record.url
        if hasattr(record, 'method'):
            log_record['method'] = record.method
            
        log_record['message'] = mask_sensitive_data(log_record['message'])
        
        # Add exception info if available
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)


def configure_logging(log_level=None):
    """
    Configure application logging.
    
    Args:
        log_level (str, optional): Logging level (DEBUG, INFO, etc.)
    """
    if log_level is None:
        log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
    
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.DEBUG
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Check if handlers are already configured to avoid duplicate logs
    if not root_logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        
        # Create formatter
        if os.environ.get('LOG_FORMAT', '').lower() == 'json':
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
            )
        
        # Add request info filter
        request_filter = RequestInfoFilter()
        console_handler.addFilter(request_filter)
        
        # Set formatter for handlers
        console_handler.setFormatter(formatter)
        
        # Add handlers to root logger
        root_logger.addHandler(console_handler)
    
    # Set level for specific loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Configure app logger
    app_logger = logging.getLogger('app')
    app_logger.setLevel(numeric_level)
    app_logger.propagate = True
    
    # Configure API logger
    api_logger = logging.getLogger('api')
    api_logger.setLevel(numeric_level)
    api_logger.propagate = True
    
    try:
        logging.info(f"Logging configured with level: {log_level}")
    except Exception as e:
        print(f"Logging configuration complete with level: {log_level}")
        print(f"Note: {e}")
