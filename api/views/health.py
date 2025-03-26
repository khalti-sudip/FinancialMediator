"""
Health Check Views Module.

This module provides endpoints for:
- System health monitoring
- Service status checks
- Resource availability verification
- Performance metrics
"""

from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import redis
import psycopg2
import logging

from api.serializers import HealthCheckSerializer

logger = logging.getLogger(__name__)

class BaseHealthCheck:
    """Base class for health check components."""
    
    def __init__(self, name):
        self.name = name
        
    def _measure_latency(self, func):
        """Measure the latency of a function call."""
        try:
            start = timezone.now()
            func()
            end = timezone.now()
            return (end - start).total_seconds() * 1000
        except Exception:
            return None
            
    def _get_status_response(self, is_healthy, error=None, extra=None):
        """Create a standardized status response."""
        response = {
            "status": "up" if is_healthy else "down",
        }
        if error:
            response["error"] = str(error)
        if extra:
            response.update(extra)
        return response

class HealthCheckView(APIView):
    """View for checking system health status."""
    
    permission_classes = []  # Allow unauthenticated access
    
    def get(self, request):
        """
        Get system health status.
        
        Checks:
        1. Database connectivity
        2. Redis connection
        3. Celery worker status
        4. System resources
        
        Returns:
            Response: Health check results
        """
        try:
            # Initialize checkers
            db_checker = DatabaseHealthCheck()
            redis_checker = RedisHealthCheck()
            celery_checker = CeleryHealthCheck()
            
            # Perform checks
            db_status = db_checker.check()
            redis_status = redis_checker.check()
            celery_status = celery_checker.check()
            
            # Prepare response
            data = {
                "status": "healthy" if all([
                    db_status["status"] == "up",
                    redis_status["status"] == "up",
                    celery_status["status"] == "up",
                ]) else "degraded",
                "timestamp": timezone.now(),
                "version": settings.VERSION,
                "services": {
                    "database": db_status,
                    "redis": redis_status,
                    "celery": celery_status,
                },
            }
            
            # Serialize and return
            serializer = HealthCheckSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error("Health check failed", exc_info=True)
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class DatabaseHealthCheck(BaseHealthCheck):
    """Health checker for database connectivity."""
    
    def __init__(self):
        super().__init__("database")
        
    def check(self):
        """Check database connectivity."""
        try:
            # Try to connect
            conn = psycopg2.connect(settings.DATABASES["default"]["NAME"])
            conn.close()
            
            latency = self._measure_latency(
                lambda: self._test_db_connection()
            )
            
            return self._get_status_response(
                is_healthy=True,
                extra={"latency": latency}
            )
            
        except Exception as e:
            logger.error("Database check failed", exc_info=True)
            return self._get_status_response(
                is_healthy=False,
                error=e
            )
            
    def _test_db_connection(self):
        """Execute a simple query to test the connection."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

class RedisHealthCheck(BaseHealthCheck):
    """Health checker for Redis connectivity."""
    
    def __init__(self):
        super().__init__("redis")
        
    def check(self):
        """Check Redis connectivity."""
        try:
            # Try to ping Redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            
            latency = self._measure_latency(
                lambda: cache.get("health_check_test")
            )
            
            return self._get_status_response(
                is_healthy=True,
                extra={"latency": latency}
            )
            
        except Exception as e:
            logger.error("Redis check failed", exc_info=True)
            return self._get_status_response(
                is_healthy=False,
                error=e
            )

class CeleryHealthCheck(BaseHealthCheck):
    """Health checker for Celery worker status."""
    
    def __init__(self):
        super().__init__("celery")
        
    def check(self):
        """Check Celery worker status."""
        try:
            # Try to inspect workers
            from celery.app import current_app
            
            inspector = current_app.control.inspect()
            workers = inspector.active()
            
            if not workers:
                return self._get_status_response(
                    is_healthy=False,
                    error="No active workers found"
                )
            
            return self._get_status_response(
                is_healthy=True,
                extra={
                    "workers": len(workers),
                    "tasks": self._get_celery_stats()
                }
            )
            
        except Exception as e:
            logger.error("Celery check failed", exc_info=True)
            return self._get_status_response(
                is_healthy=False,
                error=e
            )
            
    def _get_celery_stats(self):
        """Get Celery task statistics."""
        from celery.app import current_app
        inspector = current_app.control.inspect()
        stats = {
            "active": len(inspector.active() or {}),
            "scheduled": len(inspector.scheduled() or {}),
            "reserved": len(inspector.reserved() or {}),
        }
        return stats
