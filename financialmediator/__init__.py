"""
FinancialMediator application initialization.

This module initializes the application and sets up OpenTelemetry instrumentation.
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter

# Initialize OpenTelemetry
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(OTLPSpanExporter())
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

logger_provider = LoggerProvider()
log_processor = BatchLogRecordProcessor(OTLPLogExporter())
logger_provider.add_log_record_processor(log_processor)

# Instrumentation
DjangoInstrumentor().instrument()
RedisInstrumentor().instrument()
RequestsInstrumentor().instrument()
