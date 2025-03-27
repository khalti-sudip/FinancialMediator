"""
Logging utilities for FinancialMediator.

This module provides structured logging capabilities using OpenTelemetry.
"""

from typing import Any, Dict, Optional, Union, List
import logging
from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk._logs.severity import SeverityNumber
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.trace.status import StatusCode

# Initialize OpenTelemetry
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(OTLPSpanExporter())
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

logger_provider = LoggerProvider()
log_processor = BatchLogRecordProcessor(OTLPLogExporter())
logger_provider.add_log_record_processor(log_processor)

# Instrumentation
LoggingInstrumentor().instrument()

class Logger:
    """
    Structured logger that integrates with OpenTelemetry.
    
    Attributes:
        name: Name of the logger
        tracer: OpenTelemetry tracer
    """
    
    def __init__(self, name: str):
        """
        Initialize a structured logger.
        
        Args:
            name: Name of the logger
        """
        self.name = name
        self.tracer = trace.get_tracer(name)
        self.logger = logging.getLogger(name)
        
    def log(self, level: str, message: str, attributes: Optional[Dict[str, Any]] = None,
            request_id: Optional[str] = None, user_id: Optional[str] = None,
            context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Log a message with structured attributes.
        
        Args:
            level: Log level (e.g., 'info', 'error')
            message: Log message
            attributes: Additional attributes to log
            request_id: Request ID for correlation
            user_id: User ID for correlation
            context: Additional context information
            **kwargs: Additional keyword arguments
        """
        with self.tracer.start_as_current_span(f"log_{level}") as span:
            span.set_attribute("message", message)
            
            if request_id:
                span.set_attribute("request_id", request_id)
            if user_id:
                span.set_attribute("user_id", user_id)
            
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, value)
            
            if context:
                for key, value in context.items():
                    span.set_attribute(f"context.{key}", value)
            
            if level == 'error':
                span.set_status(StatusCode.ERROR)
                
            self.logger.log(
                getattr(logging, level.upper()),
                message,
                extra={
                    'attributes': attributes or {},
                    'request_id': request_id,
                    'user_id': user_id,
                    'context': context or {}
                }
            )
    
    def info(self, message: str, attributes: Optional[Dict[str, Any]] = None,
             request_id: Optional[str] = None, user_id: Optional[str] = None,
             context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Log an info message.
        
        Args:
            message: Info message
            attributes: Additional attributes
            request_id: Request ID
            user_id: User ID
            context: Additional context
            **kwargs: Additional keyword arguments
        """
        self.log('info', message, attributes, request_id, user_id, context, **kwargs)
    
    def error(self, message: str, attributes: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None, user_id: Optional[str] = None,
              context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Log an error message.
        
        Args:
            message: Error message
            attributes: Additional attributes
            request_id: Request ID
            user_id: User ID
            context: Additional context
            **kwargs: Additional keyword arguments
        """
        self.log('error', message, attributes, request_id, user_id, context, **kwargs)
    
    def warning(self, message: str, attributes: Optional[Dict[str, Any]] = None,
                request_id: Optional[str] = None, user_id: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Log a warning message.
        
        Args:
            message: Warning message
            attributes: Additional attributes
            request_id: Request ID
            user_id: User ID
            context: Additional context
            **kwargs: Additional keyword arguments
        """
        self.log('warning', message, attributes, request_id, user_id, context, **kwargs)
    
    def debug(self, message: str, attributes: Optional[Dict[str, Any]] = None,
              request_id: Optional[str] = None, user_id: Optional[str] = None,
              context: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Log a debug message.
        
        Args:
            message: Debug message
            attributes: Additional attributes
            request_id: Request ID
            user_id: User ID
            context: Additional context
            **kwargs: Additional keyword arguments
        """
        self.log('debug', message, attributes, request_id, user_id, context, **kwargs)

def get_logger(name: str) -> Logger:
    """
    Get a structured logger instance.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return Logger(name)

def setup_logging(config: Dict[str, Any]) -> None:
    """
    Configure the logging system.
    
    Args:
        config: Logging configuration dictionary
    """
    logging.basicConfig(
        level=config.get('level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.get('file', 'app.log'))
        ]
    )

def log_exception(exc: Exception, logger: Logger, request_id: Optional[str] = None,
                  user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an exception with structured attributes.
    
    Args:
        exc: Exception to log
        logger: Logger instance
        request_id: Request ID for correlation
        user_id: User ID for correlation
        context: Additional context information
    """
    logger.error(
        f"Exception occurred: {str(exc)}",
        attributes={
            'exception_type': type(exc).__name__,
            'exception_message': str(exc)
        },
        request_id=request_id,
        user_id=user_id,
        context=context
    )

def log_performance(metric: str, value: Union[int, float], unit: str,
                    logger: Logger, request_id: Optional[str] = None,
                    user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log performance metrics.
    
    Args:
        metric: Name of the metric
        value: Metric value
        unit: Unit of measurement
        logger: Logger instance
        request_id: Request ID for correlation
        user_id: User ID for correlation
        context: Additional context information
    """
    logger.info(
        f"Performance metric: {metric}={value}{unit}",
        attributes={
            'metric': metric,
            'value': value,
            'unit': unit
        },
        request_id=request_id,
        user_id=user_id,
        context=context
    )
