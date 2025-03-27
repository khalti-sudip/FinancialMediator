"""
OpenTelemetry instrumentation module for FinancialMediator.

This module provides comprehensive OpenTelemetry instrumentation for the application,
including tracing, metrics, and logging. It supports:

1. Django request/response tracing
2. Redis cache operations
3. PostgreSQL database queries
4. HTTP requests (using requests library)
5. Celery task execution
6. Structured logging

The instrumentation is configured using environment variables:
- OTEL_SERVICE_NAME: Name of the service (default: financial-mediator)
- OTEL_SERVICE_VERSION: Version of the service (default: 1.0.0)
- OTEL_DEPLOYMENT_ENVIRONMENT: Deployment environment (default: production)
- OTEL_EXPORTER_OTLP_ENDPOINT: Optional OTLP endpoint for exporting traces
- OTEL_LOG_LEVEL: Logging level (default: INFO)
"""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
import os
import logging
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

def configure_opentelemetry():
    """
    Configure OpenTelemetry for the application.
    
    This function sets up:
    1. Tracer provider with resource attributes
    2. Meter provider for metrics
    3. Logger provider for structured logging
    4. OTLP exporters for trace, metric, and log export
    5. Instrumentation for all supported components
    
    The configuration is controlled by environment variables:
    - OTEL_SERVICE_NAME: Service name (required)
    - OTEL_SERVICE_VERSION: Service version (required)
    - OTEL_DEPLOYMENT_ENVIRONMENT: Deployment environment (required)
    - OTEL_EXPORTER_OTLP_ENDPOINT: Optional OTLP endpoint URL
    - OTEL_LOG_LEVEL: Logging level (default: INFO)
    """
    # Get environment variables
    env = os.environ
    
    # Create resource with service information
    from opentelemetry.sdk.resources import Resource
    resource = Resource(attributes={
        "service.name": env.get("OTEL_SERVICE_NAME", "financial-mediator"),
        "service.version": env.get("OTEL_SERVICE_VERSION", "1.0.0"),
        "deployment.environment": env.get("OTEL_DEPLOYMENT_ENVIRONMENT", "production")
    })
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Create meter provider
    meter_provider = MeterProvider(resource=resource)
    
    # Create logger provider
    logger_provider = LoggerProvider(resource=resource)
    
    # Set up exporters
    exporters = []
    metric_exporters = []
    log_exporters = []
    
    # OTLP HTTP exporter
    if env.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        # Traces
        exporters.append(OTLPSpanExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers=env.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        ))
        
        # Metrics
        metric_exporters.append(OTLPMetricExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers=env.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        ))
        
        # Logs
        log_exporters.append(OTLPLogExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers=env.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        ))
    
    # Add processors
    tracer_provider.add_span_processor(BatchSpanProcessor(*exporters))
    meter_provider.add_reader(PeriodicExportingMetricReader(*metric_exporters))
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(*log_exporters))
    
    # Set the global providers
    trace.set_tracer_provider(tracer_provider)
    metrics.set_meter_provider(meter_provider)
    
    # Configure logging
    logging.basicConfig(
        level=env.get("OTEL_LOG_LEVEL", "INFO"),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create OpenTelemetry logging handler
    otel_handler = LoggingHandler(
        level=env.get("OTEL_LOG_LEVEL", "INFO"),
        logger_provider=logger_provider
    )
    
    # Add OpenTelemetry handler to root logger
    logging.getLogger().addHandler(otel_handler)
    
    # Instrument Django
    DjangoInstrumentor().instrument()
    
    # Instrument Redis
    RedisInstrumentor().instrument()
    
    # Instrument PostgreSQL
    Psycopg2Instrumentor().instrument()
    
    # Instrument HTTP requests
    RequestsInstrumentor().instrument()
    
    # Instrument Celery
    CeleryInstrumentor().instrument()

# Configure OpenTelemetry when the module is imported
configure_opentelemetry()
