"""
Utility functions for structured logging using OpenTelemetry.

This module provides helper functions to create structured logs with context
and attributes that can be easily correlated with traces and metrics.
"""

import logging
from opentelemetry import trace
from opentelemetry.sdk._logs.severity import SeverityNumber
from typing import Dict, Any

# Get the global tracer
tracer = trace.get_tracer(__name__)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with OpenTelemetry integration.
    
    Args:
        name: Name of the logger
    
    Returns:
        A logger instance configured with OpenTelemetry
    """
    logger = logging.getLogger(name)
    return logger

def log_info(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log an info message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_info") as span:
        span.set_attribute("message", message)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        logger.info(message, extra={"attributes": attributes, **kwargs})

def log_error(
    logger: logging.Logger,
    message: str,
    exception: Exception = None,
    attributes: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log an error message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        exception: Optional exception to log
        attributes: Additional attributes for the log
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_error", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        if exception:
            span.set_attribute("exception.type", type(exception).__name__)
            span.set_attribute("exception.message", str(exception))
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        logger.error(message, extra={"attributes": attributes, **kwargs}, exc_info=exception)

def log_warning(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log a warning message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_warning", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        logger.warning(message, extra={"attributes": attributes, **kwargs})

def log_debug(
    logger: logging.Logger,
    message: str,
    attributes: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log a debug message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        attributes: Additional attributes for the log
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_debug", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        logger.debug(message, extra={"attributes": attributes, **kwargs})

def log_critical(
    logger: logging.Logger,
    message: str,
    exception: Exception = None,
    attributes: Dict[str, Any] = None,
    **kwargs
) -> None:
    """
    Log a critical message with structured attributes.
    
    Args:
        logger: Logger instance
        message: Message to log
        exception: Optional exception to log
        attributes: Additional attributes for the log
        **kwargs: Additional keyword arguments
    """
    with tracer.start_as_current_span("log_critical", kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute("message", message)
        if exception:
            span.set_attribute("exception.type", type(exception).__name__)
            span.set_attribute("exception.message", str(exception))
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        logger.critical(message, extra={"attributes": attributes, **kwargs}, exc_info=exception)
