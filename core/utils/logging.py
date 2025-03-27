"""
Utility functions for structured logging using OpenTelemetry.

This module provides helper functions to create structured logs with context
and attributes that can be easily correlated with traces and metrics.
"""

import logging
import traceback
from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider, LogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs.severity import SeverityNumber
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import get_current_span
from typing import Dict, Any, Optional, Type
import json
from datetime import datetime

# Initialize OpenTelemetry Logger
resource = Resource(attributes={
    "service.name": "financialmediator",
    "service.version": "1.0.0"
})

logger_provider = LoggerProvider(resource=resource)
log_processor = BatchLogRecordProcessor()
logger_provider.add_log_record_processor(log_processor)

# Get the global tracer
tracer = trace.get_tracer(__name__)

class LogContext:
    """
    Context manager for adding context to logs within a block.
    """
    def __init__(self, logger: logging.Logger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
        self.span = None

    def __enter__(self):
        self.span = tracer.start_as_current_span("log_context")
        for key, value in self.context.items():
            self.span.set_attribute(key, value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.span.set_attribute("exception.type", str(exc_type))
            self.span.set_attribute("exception.message", str(exc_val))
        self.span.end()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with OpenTelemetry integration.
    
    Args:
        name: Name of the logger
    
    Returns:
        A logger instance configured with OpenTelemetry
    """
    logger = logging.getLogger(name)
    
    # Add OpenTelemetry handler
    class OtelHandler(logging.Handler):
        def emit(self, record):
            span = get_current_span()
            
            log_record = LogRecord(
                timestamp=datetime.utcnow().timestamp(),
                trace_id=span.get_span_context().trace_id,
                span_id=span.get_span_context().span_id,
                severity_number=SeverityNumber.INFO,
                attributes={
                    "message": record.getMessage(),
                    "level": record.levelname,
                    "logger": record.name,
                    "file": record.filename,
                    "line": record.lineno,
                    **record.__dict__.get("attributes", {})
                }
            )
            
            logger_provider.emit(log_record)
    
    handler = OtelHandler()
    logger.addHandler(handler)
    
    return logger

def format_log_message(
    message: str,
    level: str,
    attributes: Dict[str, Any],
    **kwargs
) -> str:
    """
    Format log message in JSON structure.
    
    Args:
        message: The log message
        level: Log level (INFO, ERROR, etc.)
        attributes: Additional attributes
        **kwargs: Additional keyword arguments
    
    Returns:
        str: Formatted JSON log message
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "attributes": attributes,
        **kwargs
    }
    return json.dumps(log_data)

def log_info(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log an info message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        request_id: Request ID for correlation
        user_id: User ID for context
        context: Additional context information
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_info") as span:
        span.set_attribute("message", message)
        span.set_attribute("level", "INFO")
        
        # Add standard context
        if request_id:
            span.set_attribute("request_id", request_id)
        if user_id:
            span.set_attribute("user_id", user_id)
        
        # Add attributes and context
        combined_attributes = {}
        if attributes:
            combined_attributes.update(attributes)
        if context:
            combined_attributes.update(context)
        
        for key, value in combined_attributes.items():
            span.set_attribute(key, value)
            
        formatted_message = format_log_message(
            message=message,
            level="INFO",
            attributes=combined_attributes,
            request_id=request_id,
            user_id=user_id
        )
        
        logger.info(formatted_message, extra={"attributes": combined_attributes, **kwargs})

def log_error(
    logger: logging.Logger,
    message: str,
    exception: Optional[Exception] = None,
    attributes: Dict[str, Any] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log an error message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        exception: Optional exception to log
        attributes: Additional attributes for the log
        request_id: Request ID for correlation
        user_id: User ID for context
        context: Additional context information
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_error", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        span.set_attribute("level", "ERROR")
        
        # Add standard context
        if request_id:
            span.set_attribute("request_id", request_id)
        if user_id:
            span.set_attribute("user_id", user_id)
        
        # Add exception details
        if exception:
            span.set_attribute("exception.type", type(exception).__name__)
            span.set_attribute("exception.message", str(exception))
            span.set_attribute("exception.traceback", traceback.format_exc())
        
        # Add attributes and context
        combined_attributes = {}
        if attributes:
            combined_attributes.update(attributes)
        if context:
            combined_attributes.update(context)
        
        for key, value in combined_attributes.items():
            span.set_attribute(key, value)
            
        formatted_message = format_log_message(
            message=message,
            level="ERROR",
            attributes=combined_attributes,
            request_id=request_id,
            user_id=user_id
        )
        
        logger.error(
            formatted_message,
            extra={"attributes": combined_attributes, **kwargs},
            exc_info=exception
        )

def log_warning(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log a warning message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        request_id: Request ID for correlation
        user_id: User ID for context
        context: Additional context information
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_warning", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        span.set_attribute("level", "WARNING")
        
        # Add standard context
        if request_id:
            span.set_attribute("request_id", request_id)
        if user_id:
            span.set_attribute("user_id", user_id)
        
        # Add attributes and context
        combined_attributes = {}
        if attributes:
            combined_attributes.update(attributes)
        if context:
            combined_attributes.update(context)
        
        for key, value in combined_attributes.items():
            span.set_attribute(key, value)
            
        formatted_message = format_log_message(
            message=message,
            level="WARNING",
            attributes=combined_attributes,
            request_id=request_id,
            user_id=user_id
        )
        
        logger.warning(
            formatted_message,
            extra={"attributes": combined_attributes, **kwargs}
        )

def log_debug(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    context: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log a debug message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        request_id: Request ID for correlation
        user_id: User ID for context
        context: Additional context information
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_debug", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        span.set_attribute("level", "DEBUG")
        
        # Add standard context
        if request_id:
            span.set_attribute("request_id", request_id)
        if user_id:
            span.set_attribute("user_id", user_id)
        
        # Add attributes and context
        combined_attributes = {}
        if attributes:
            combined_attributes.update(attributes)
        if context:
            combined_attributes.update(context)
        
        for key, value in combined_attributes.items():
            span.set_attribute(key, value)
            
        formatted_message = format_log_message(
            message=message,
            level="DEBUG",
            attributes=combined_attributes,
            request_id=request_id,
            user_id=user_id
        )
        
        logger.debug(
            formatted_message,
            extra={"attributes": combined_attributes, **kwargs}
        )
