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
            # Check database
            db_status = self._check_database()
            
            # Check Redis
            redis_status = self._check_redis()
            
            # Check Celery
            celery_status = self._check_celery()
            
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
    
    def _check_database(self):
        """
        Check database connectivity.
        
        Returns:
            dict: Database status information
        """
        try:
            # Try to connect
            conn = psycopg2.connect(settings.DATABASES["default"]["NAME"])
            conn.close()
            
            return {
                "status": "up",
                "latency": self._measure_db_latency(),
            }
            
        except Exception as e:
            logger.error("Database check failed", exc_info=True)
            return {
                "status": "down",
                "error": str(e),
            }
    
    def _check_redis(self):
        """
        Check Redis connectivity.
        
        Returns:
            dict: Redis status information
        """
        try:
            # Try to ping Redis
            redis_client = redis.from_url(settings.REDIS_URL)
            redis_client.ping()
            
            return {
                "status": "up",
                "latency": self._measure_redis_latency(),
            }
            
        except Exception as e:
            logger.error("Redis check failed", exc_info=True)
            return {
                "status": "down",
                "error": str(e),
            }
    
    def _check_celery(self):
        """
        Check Celery worker status.
        
        Returns:
            dict: Celery status information
        """
        try:
            # Try to inspect workers
            from celery.app import current_app
            
            inspector = current_app.control.inspect()
            workers = inspector.active()
            
            if not workers:
                return {
                    "status": "down",
                    "error": "No active workers found",
                }
            
            return {
                "status": "up",
                "workers": len(workers),
                "tasks": self._get_celery_stats(),
            }
            
        except Exception as e:
            logger.error("Celery check failed", exc_info=True)
            return {
                "status": "down",
                "error": str(e),
            }
    
    def _measure_db_latency(self):
        """
        Measure database query latency.
        
        Returns:
            float: Query latency in milliseconds
        """
        try:
            start = timezone.now()
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            end = timezone.now()
            
            return (end - start).total_seconds() * 1000
            
        except Exception:
            return None
    
    def _measure_redis_latency(self):
        """
        Measure Redis operation latency.
        
        Returns:
            float: Operation latency in milliseconds
        """
        try:
            start = timezone.now()
            cache.get("health_check_test")
            end = timezone.now()
            
            return (end - start).total_seconds() * 1000
            
        except Exception:
            return None
    
    def _get_celery_stats(self):
        """
        Get Celery task statistics.
        
        Returns:
            dict: Task statistics
        """
        try:
            stats = cache.get("celery_stats") or {}
            return {
                "processed": stats.get("processed", 0),
                "failed": stats.get("failed", 0),
                "active": stats.get("active", 0),
            }
            
        except Exception:
            return {}
