
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
import logging

logger = logging.getLogger(__name__)

def setup_telemetry():
    # Resource attributes for service identification
    resource = Resource.create({"service.name": "banking-api"})
    
    # Configure tracing
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # Configure metrics with Prometheus exporter
    reader = PrometheusMetricReader()
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)
    
    # Start Prometheus metrics server
    start_http_server(port=9090, addr="0.0.0.0")
    
    # Instrument Django
    DjangoInstrumentor().instrument()
    
    # Instrument logging
    LoggingInstrumentor().instrument()
    
    # Instrument HTTP requests
    RequestsInstrumentor().instrument()
    
    logger.info("Telemetry setup completed")
