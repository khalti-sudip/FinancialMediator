"""
Telemetry utilities for tracking application metrics and events.
"""

import os
import logging
from datetime import datetime
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

logger = logging.getLogger(__name__)

class Telemetry:
    """Class for collecting and sending telemetry data."""
    
    def __init__(self):
        """Initialize telemetry with default values."""
        self.instance_id = os.environ.get("INSTANCE_ID", "local")
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.timestamp = datetime.utcnow()
        
        # Enhanced resource attributes for better service identification
        resource = Resource.create(
            {
                "service.name": "banking-api",
                "service.instance.id": self.instance_id,
                "deployment.environment": self.environment,
                "host.name": os.environ.get("HOST_NAME", "unknown"),
                "service.version": os.environ.get("SERVICE_VERSION", "1.0.0"),
            }
        )

        # Configure tracing with sampling
        sampler = ParentBasedTraceIdRatio(rate=0.5)  # Sample 50% of traces
        tracer_provider = TracerProvider(resource=resource, sampler=sampler)
        trace.set_tracer_provider(tracer_provider)

        # Configure metrics with enhanced Prometheus exporter
        reader = PrometheusMetricReader()
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[reader],
            metric_interval=5000,  # 5 second collection interval
        )
        metrics.set_meter_provider(meter_provider)

        # Start Prometheus metrics server
        start_http_server(port=9090, addr="0.0.0.0")

        # Instrument Django with distributed tracing
        DjangoInstrumentor().instrument(
            is_distributed=True, excluded_urls="^/healthz,^/metrics"
        )

        # Enhanced logging instrumentation
        LoggingInstrumentor().instrument(set_logging_format=True, log_level=logging.INFO)

        # Configure request instrumentation with retry and timeout
        RequestsInstrumentor().instrument(
            tracer_provider=tracer_provider,
            span_callback=lambda span: span.set_attribute(
                "service.version", os.environ.get("SERVICE_VERSION", "1.0.0")
            ),
        )

        logger.info("Telemetry setup completed for distributed environment")

    def track_event(self, event_name: str, properties: dict = None):
        """
        Track an event with associated properties.
        
        Args:
            event_name (str): Name of the event
            properties (dict, optional): Additional properties to track
        """
        event_data = {
            "event_name": event_name,
            "timestamp": self.timestamp.isoformat(),
            "instance_id": self.instance_id,
            "environment": self.environment,
            "properties": properties or {},
        }
        
        logger.info(f"Tracking event: {event_data}")
        
        # TODO: Implement actual telemetry sending
        # This could be to a metrics service, database, or logging system
        
    def track_metric(self, metric_name: str, value: float, tags: dict = None):
        """
        Track a numeric metric with associated tags.
        
        Args:
            metric_name (str): Name of the metric
            value (float): Metric value
            tags (dict, optional): Additional tags to associate with the metric
        """
        metric_data = {
            "metric_name": metric_name,
            "value": value,
            "timestamp": self.timestamp.isoformat(),
            "instance_id": self.instance_id,
            "environment": self.environment,
            "tags": tags or {},
        }
        
        logger.info(f"Tracking metric: {metric_data}")
        
        # TODO: Implement actual metric sending
        # This could be to a metrics service, database, or logging system
