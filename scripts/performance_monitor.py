"""
Performance monitoring script for FinancialMediator.

This script provides tools for monitoring and profiling the application's performance.
"""

import os
import time
import json
from typing import Dict, Any, List
import logging
from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize OpenTelemetry
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(OTLPSpanExporter())
tracer_provider.add_span_processor(span_processor)

logger_provider = LoggerProvider()
log_processor = BatchLogRecordProcessor(OTLPLogExporter())
logger_provider.add_log_record_processor(log_processor)

# Instrumentation
DjangoInstrumentor().instrument()
RedisInstrumentor().instrument()
RequestsInstrumentor().instrument()

class PerformanceMonitor:
    """
    Performance monitoring class for tracking application metrics.
    """
    
    def __init__(self):
        self.tracer = tracer_provider.get_tracer(__name__)
        self.logger = logger_provider.get_logger(__name__)
        self.metrics = {
            'transaction_times': [],
            'api_response_times': [],
            'database_queries': [],
            'cache_hits': [],
            'cache_misses': []
        }
    
    def start_transaction_monitor(self):
        """
        Start monitoring transaction performance.
        """
        with self.tracer.start_as_current_span("transaction_monitor") as span:
            span.set_attribute("monitor_type", "transaction")
            span.set_attribute("start_time", time.time())
            
    def record_transaction_time(self, duration: float):
        """
        Record transaction processing time.
        
        Args:
            duration: Transaction duration in seconds
        """
        self.metrics['transaction_times'].append(duration)
        self.logger.info(
            "Transaction processed",
            extra={
                "duration": duration,
                "timestamp": time.time()
            }
        )
    
    def start_api_monitor(self, endpoint: str):
        """
        Start monitoring API endpoint performance.
        
        Args:
            endpoint: API endpoint path
        """
        with self.tracer.start_as_current_span(f"api_monitor_{endpoint}") as span:
            span.set_attribute("monitor_type", "api")
            span.set_attribute("endpoint", endpoint)
            span.set_attribute("start_time", time.time())
            
    def record_api_response(self, endpoint: str, duration: float):
        """
        Record API response time.
        
        Args:
            endpoint: API endpoint path
            duration: Response duration in seconds
        """
        self.metrics['api_response_times'].append({
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': time.time()
        })
        self.logger.info(
            "API response recorded",
            extra={
                "endpoint": endpoint,
                "duration": duration,
                "timestamp": time.time()
            }
        )
    
    def record_database_query(self, query: str, duration: float):
        """
        Record database query performance.
        
        Args:
            query: SQL query string
            duration: Query duration in seconds
        """
        self.metrics['database_queries'].append({
            'query': query,
            'duration': duration,
            'timestamp': time.time()
        })
        self.logger.info(
            "Database query executed",
            extra={
                "query": query,
                "duration": duration,
                "timestamp": time.time()
            }
        )
    
    def record_cache_hit(self, key: str):
        """
        Record cache hit.
        
        Args:
            key: Cache key
        """
        self.metrics['cache_hits'].append({
            'key': key,
            'timestamp': time.time()
        })
        self.logger.info(
            "Cache hit",
            extra={
                "key": key,
                "timestamp": time.time()
            }
        )
    
    def record_cache_miss(self, key: str):
        """
        Record cache miss.
        
        Args:
            key: Cache key
        """
        self.metrics['cache_misses'].append({
            'key': key,
            'timestamp': time.time()
        })
        self.logger.warning(
            "Cache miss",
            extra={
                "key": key,
                "timestamp": time.time()
            }
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary of performance metrics
        """
        return {
            'transaction_times': self.metrics['transaction_times'],
            'api_response_times': self.metrics['api_response_times'],
            'database_queries': self.metrics['database_queries'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses']
        }
    
    def save_metrics(self, filename: str = 'performance_metrics.json'):
        """
        Save performance metrics to a file.
        
        Args:
            filename: Output filename
        """
        metrics = self.get_performance_metrics()
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=4)
    
    def analyze_bottlenecks(self) -> Dict[str, Any]:
        """
        Analyze performance metrics to identify potential bottlenecks.
        
        Returns:
            Dictionary of potential bottlenecks
        """
        metrics = self.get_performance_metrics()
        
        bottlenecks = {
            'slow_transactions': [
                t for t in metrics['transaction_times']
                if t > 2.0  # Threshold for slow transactions
            ],
            'slow_api_endpoints': {
                endpoint: [
                    r for r in metrics['api_response_times']
                    if r['duration'] > 1.0 and r['endpoint'] == endpoint
                ]
                for endpoint in set(
                    r['endpoint'] for r in metrics['api_response_times']
                )
            },
            'slow_queries': [
                q for q in metrics['database_queries']
                if q['duration'] > 0.5  # Threshold for slow queries
            ],
            'cache_miss_ratio': len(metrics['cache_misses']) / (
                len(metrics['cache_hits']) + len(metrics['cache_misses'])
            ) if metrics['cache_hits'] or metrics['cache_misses'] else 0
        }
        
        return bottlenecks

def main():
    """
    Run performance monitoring.
    """
    monitor = PerformanceMonitor()
    
    try:
        # Example usage
        monitor.start_transaction_monitor()
        time.sleep(1)  # Simulate transaction
        monitor.record_transaction_time(1.2)
        
        monitor.start_api_monitor("/api/transactions")
        time.sleep(0.5)  # Simulate API response
        monitor.record_api_response("/api/transactions", 0.5)
        
        # Simulate database query
        monitor.record_database_query("SELECT * FROM transactions", 0.2)
        
        # Simulate cache operations
        monitor.record_cache_hit("user_123")
        monitor.record_cache_miss("user_456")
        
        # Analyze performance
        bottlenecks = monitor.analyze_bottlenecks()
        
        # Save metrics
        monitor.save_metrics()
        
        # Print analysis
        print("\nPerformance Analysis:")
        print("====================")
        
        # Transaction performance
        print(f"\nTransactions: {len(monitor.metrics['transaction_times'])}")
        if bottlenecks['slow_transactions']:
            print(f"Slow transactions: {len(bottlenecks['slow_transactions'])}")
        
        # API performance
        print(f"\nAPI Endpoints: {len(monitor.metrics['api_response_times'])}")
        for endpoint, responses in bottlenecks['slow_api_endpoints'].items():
            if responses:
                print(f"Slow responses for {endpoint}: {len(responses)}")
        
        # Database queries
        print(f"\nDatabase Queries: {len(monitor.metrics['database_queries'])}")
        if bottlenecks['slow_queries']:
            print(f"Slow queries: {len(bottlenecks['slow_queries'])}")
        
        # Cache performance
        print(f"\nCache Hits: {len(monitor.metrics['cache_hits'])}")
        print(f"Cache Misses: {len(monitor.metrics['cache_misses'])}")
        print(f"Cache Miss Ratio: {bottlenecks['cache_miss_ratio']:.2%}")
        
    except Exception as e:
        logging.error(f"Error in performance monitoring: {str(e)}")

if __name__ == "__main__":
    main()
