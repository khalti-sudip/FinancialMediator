
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from prometheus_client import start_http_server
import logging
import os

logger = logging.getLogger(__name__)

def setup_telemetry():
    # Enhanced resource attributes for better service identification
    resource = Resource.create({
        "service.name": "banking-api",
        "service.instance.id": os.environ.get("REPLIT_DEPLOYMENT_ID", "local"),
        "deployment.environment": "production" if os.environ.get("REPLIT_DEPLOYMENT") else "development",
        "host.name": os.environ.get("REPL_SLUG", "unknown"),
        "service.version": os.environ.get("REPL_VERSION", "1.0.0")
    })
    
    # Configure tracing with sampling
    sampler = ParentBasedTraceIdRatio(rate=0.5)  # Sample 50% of traces
    tracer_provider = TracerProvider(
        resource=resource,
        sampler=sampler
    )
    trace.set_tracer_provider(tracer_provider)
    
    # Configure metrics with enhanced Prometheus exporter
    reader = PrometheusMetricReader()
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[reader],
        metric_interval=5000  # 5 second collection interval
    )
    metrics.set_meter_provider(meter_provider)
    
    # Start Prometheus metrics server
    start_http_server(port=9090, addr="0.0.0.0")
    
    # Instrument Django with distributed tracing
    DjangoInstrumentor().instrument(
        is_distributed=True,
        excluded_urls="^/healthz,^/metrics"
    )
    
    # Enhanced logging instrumentation
    LoggingInstrumentor().instrument(
        set_logging_format=True,
        log_level=logging.INFO
    )
    
    # Configure request instrumentation with retry and timeout
    RequestsInstrumentor().instrument(
        tracer_provider=tracer_provider,
        span_callback=lambda span: span.set_attribute("service.version", os.environ.get("REPL_VERSION", "1.0.0"))
    )
    
    logger.info("Telemetry setup completed for distributed environment")
