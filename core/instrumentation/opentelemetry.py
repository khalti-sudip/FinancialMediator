"""
OpenTelemetry instrumentation module for FinancialMediator.

This module provides comprehensive OpenTelemetry instrumentation for the application,
including tracing and metrics collection. It supports:

1. Django request/response tracing
2. Redis cache operations
3. PostgreSQL database queries
4. HTTP requests (using requests library)
5. Celery task execution

The instrumentation is configured using environment variables:
- OTEL_SERVICE_NAME: Name of the service (default: financial-mediator)
- OTEL_SERVICE_VERSION: Version of the service (default: 1.0.0)
- OTEL_DEPLOYMENT_ENVIRONMENT: Deployment environment (default: production)
- OTEL_EXPORTER_OTLP_ENDPOINT: Optional OTLP endpoint for exporting traces
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
import os

def configure_opentelemetry():
    """
    Configure OpenTelemetry for the application.
    
    This function sets up:
    1. Tracer provider with resource attributes
    2. OTLP exporter for trace export
    3. Instrumentation for all supported components
    
    The configuration is controlled by environment variables:
    - OTEL_SERVICE_NAME: Service name (required)
    - OTEL_SERVICE_VERSION: Service version (required)
    - OTEL_DEPLOYMENT_ENVIRONMENT: Deployment environment (required)
    - OTEL_EXPORTER_OTLP_ENDPOINT: Optional OTLP endpoint URL
    """
    # Get environment variables
    env = os.environ
    
    # Create resource with service information
    resource = Resource(attributes={
        "service.name": env.get("OTEL_SERVICE_NAME", "financial-mediator"),
        "service.version": env.get("OTEL_SERVICE_VERSION", "1.0.0"),
        "deployment.environment": env.get("OTEL_DEPLOYMENT_ENVIRONMENT", "production")
    })
    
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)
    
    # Set up exporters
    exporters = []
    
    # OTLP HTTP exporter
    if env.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        exporters.append(OTLPSpanExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers=env.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        ))
    
    # Add processors
    tracer_provider.add_span_processor(BatchSpanProcessor(*exporters))
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
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
