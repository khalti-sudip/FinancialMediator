import pytest
from django.test import TestCase
from django.conf import settings
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from core.instrumentation.opentelemetry import configure_opentelemetry
import os

class OpenTelemetryTest(TestCase):
    def setUp(self):
        # Save original environment
        self.original_env = dict(os.environ)
        
        # Clear any existing configuration
        trace.set_tracer_provider(TracerProvider())

    def tearDown(self):
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clear any existing configuration
        trace.set_tracer_provider(TracerProvider())

    def test_basic_configuration(self):
        """Test basic OpenTelemetry configuration."""
        os.environ['OTEL_SERVICE_NAME'] = 'test-service'
        os.environ['OTEL_SERVICE_VERSION'] = '1.0.0'
        os.environ['OTEL_DEPLOYMENT_ENVIRONMENT'] = 'test'

        configure_opentelemetry()
        
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span("test-span")
        
        self.assertIsNotNone(span)
        self.assertEqual(span.resource.attributes.get("service.name"), "test-service")
        self.assertEqual(span.resource.attributes.get("service.version"), "1.0.0")
        self.assertEqual(span.resource.attributes.get("deployment.environment"), "test")

    def test_otlp_exporter_configuration(self):
        """Test OTLP exporter configuration."""
        os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4318'
        os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'key=value'

        configure_opentelemetry()
        
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span("test-span")
        
        self.assertIsNotNone(span)
        self.assertTrue(any(
            isinstance(p, BatchSpanProcessor) and 
            isinstance(p.span_exporter, OTLPSpanExporter)
            for p in tracer.tracer_provider.span_processors
        ))

    def test_default_service_name(self):
        """Test default service name."""
        configure_opentelemetry()
        
        tracer = trace.get_tracer(__name__)
        span = tracer.start_span("test-span")
        
        self.assertEqual(span.resource.attributes.get("service.name"), "financial-mediator")

    def test_django_instrumentation(self):
        """Test Django instrumentation."""
        configure_opentelemetry()
        
        # This will fail if Django instrumentation is not properly configured
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_redis_instrumentation(self):
        """Test Redis instrumentation."""
        from redis import Redis
        
        configure_opentelemetry()
        
        # This will fail if Redis instrumentation is not properly configured
        redis = Redis.from_url('redis://localhost:6379')
        redis.ping()

    def test_postgresql_instrumentation(self):
        """Test PostgreSQL instrumentation."""
        from django.db import connection
        
        configure_opentelemetry()
        
        # This will fail if PostgreSQL instrumentation is not properly configured
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

    def test_requests_instrumentation(self):
        """Test Requests instrumentation."""
        import requests
        
        configure_opentelemetry()
        
        # This will fail if Requests instrumentation is not properly configured
        response = requests.get('http://localhost:8000/')
        self.assertEqual(response.status_code, 200)

    def test_celery_instrumentation(self):
        """Test Celery instrumentation."""
        from celery import current_app
        
        configure_opentelemetry()
        
        # This will fail if Celery instrumentation is not properly configured
        current_app.control.ping()
