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

import os
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
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

def configure_opentelemetry():
    """
    Configure OpenTelemetry for the application.
    """
    # Get environment variables
    env = os.environ
    
    # Create resource with service information
    resource = Resource(attributes={
        "service.name": env.get("OTEL_SERVICE_NAME", "financial-mediator"),
        "service.version": env.get("OTEL_SERVICE_VERSION", "1.0.0"),
        "deployment.environment": env.get("OTEL_DEPLOYMENT_ENVIRONMENT", "production"),
    })
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Set up exporters
    exporters = []
    
    # Console exporter for development
    if env.get("OTEL_EXPORTER_CONSOLE", "false").lower() == "true":
        from opentelemetry.exporter.otlp.proto.console.trace_exporter import OTLPSpanExporter
        exporters.append(OTLPSpanExporter())
    
    # OTLP exporter for production
    otlp_endpoint = env.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        exporters.append(
            OTLPSpanExporter(
                endpoint=otlp_endpoint,
                insecure=env.get("OTEL_EXPORTER_OTLP_INSECURE", "false").lower() == "true",
                credentials=env.get("OTEL_EXPORTER_OTLP_GRPC_CREDENTIALS")
            )
        )
    
    # Add exporters to the tracer provider
    for exporter in exporters:
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrumentations
    DjangoInstrumentor().instrument(
        is_distributed=True,
        excluded_urls="^/healthz,^/metrics"
    )
    RedisInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_level=env.get("OTEL_LOG_LEVEL", "INFO")
    )

# Configure OpenTelemetry when the module is imported
configure_opentelemetry()
