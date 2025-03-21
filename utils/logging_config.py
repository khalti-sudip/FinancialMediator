import os
import logging
import logging.handlers
import json
from datetime import datetime
from flask import current_app


class RequestInfoFilter(logging.Filter):
    """
    Filter to add request-specific information to log records.
    """
    def filter(self, record):
        from flask import has_request_context, g, request
        
        if has_request_context():
            record.request_id = getattr(g, 'request_id', 'no_request_id')
            record.remote_addr = request.remote_addr
            record.url = request.path
            record.method = request.method
        else:
            record.request_id = 'no_request_id'
            record.remote_addr = 'no_remote_addr'
            record.url = 'no_url'
            record.method = 'no_method'
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
        
        # Add request info if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'remote_addr'):
            log_record['remote_addr'] = record.remote_addr
        if hasattr(record, 'url'):
            log_record['url'] = record.url
        if hasattr(record, 'method'):
            log_record['method'] = record.method
        
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
