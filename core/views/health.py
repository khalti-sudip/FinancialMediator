"""
Health check views for FinancialMediator.

This module provides endpoints for monitoring the health of the application.
"""

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from opentelemetry import trace
from typing import Dict, Any
import json
import logging

# Get the global tracer
tracer = trace.get_tracer(__name__)

class HealthCheckView(View):
    """
    Health check view that verifies the application is running properly.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request) -> JsonResponse:
        """
        Check the health of the application.
        
        Returns:
            JsonResponse: Health check response
        """
        with tracer.start_as_current_span("health_check") as span:
            span.set_attribute("endpoint", "health_check")
            
            try:
                # Check database connection
                from django.db import connections
                db_conn = connections['default']
                db_conn.cursor()
                
                # Check Redis connection
                import redis
                redis_client = redis.from_url(os.getenv('REDIS_URL'))
                redis_client.ping()
                
                # Check Celery connection
                from celery import current_app
                current_app.control.ping()
                
                # Check OpenTelemetry
                from opentelemetry.sdk._logs import LoggerProvider
                logger_provider = LoggerProvider()
                logger = logger_provider.get_logger(__name__)
                logger.info("Health check passed")
                
                return JsonResponse({
                    'status': 'healthy',
                    'database': 'connected',
                    'redis': 'connected',
                    'celery': 'connected',
                    'otel': 'connected'
                })
                
            except Exception as e:
                logging.error(f"Health check failed: {str(e)}")
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                
                return JsonResponse({
                    'status': 'unhealthy',
                    'error': str(e)
                }, status=503)

class MetricsView(View):
    """
    Metrics view that provides application metrics.
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request) -> JsonResponse:
        """
        Get application metrics.
        
        Returns:
            JsonResponse: Metrics response
        """
        with tracer.start_as_current_span("metrics") as span:
            span.set_attribute("endpoint", "metrics")
            
            try:
                # Get system metrics
                import psutil
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent()
                
                # Get database metrics
                from django.db import connections
                db_conn = connections['default']
                db_metrics = {
                    'connections': len(db_conn.queries),
                    'queries': len(db_conn.queries)
                }
                
                # Get Redis metrics
                import redis
                redis_client = redis.from_url(os.getenv('REDIS_URL'))
                redis_info = redis_client.info()
                
                return JsonResponse({
                    'system': {
                        'memory': {
                            'total': memory.total,
                            'used': memory.used,
                            'percent': memory.percent
                        },
                        'cpu': {
                            'percent': cpu
                        }
                    },
                    'database': db_metrics,
                    'redis': {
                        'used_memory': redis_info.get('used_memory', 0),
                        'connected_clients': redis_info.get('connected_clients', 0),
                        'commands_processed': redis_info.get('total_commands_processed', 0)
                    }
                })
                
            except Exception as e:
                logging.error(f"Metrics collection failed: {str(e)}")
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                
                return JsonResponse({
                    'status': 'error',
                    'error': str(e)
                }, status=503)
