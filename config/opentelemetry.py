import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor


def configure_opentelemetry():
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
        exporters.append(ConsoleSpanExporter())
    
    # OTLP HTTP exporter
    if env.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        exporters.append(OTLPSpanExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
            headers=env.get("OTEL_EXPORTER_OTLP_HEADERS", "")
        ))
    
    # OTLP gRPC exporter
    if env.get("OTEL_EXPORTER_OTLP_GRPC_ENDPOINT"):
        exporters.append(GRPCSpanExporter(
            endpoint=env.get("OTEL_EXPORTER_OTLP_GRPC_ENDPOINT"),
            credentials=env.get("OTEL_EXPORTER_OTLP_GRPC_CREDENTIALS")
        ))
    
    # Add exporters to the tracer provider
    for exporter in exporters:
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    
    # Set the global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Instrumentations
    DjangoInstrumentor().instrument()
    RedisInstrumentor().instrument()
    Psycopg2Instrumentor().instrument()
    RequestsInstrumentor().instrument()
    CeleryInstrumentor().instrument()
    LoggingInstrumentor().instrument()

# Configure OpenTelemetry when the module is imported
configure_opentelemetry()
