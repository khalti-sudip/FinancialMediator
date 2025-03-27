"""
Health check views for FinancialMediator.

This module provides health check endpoints for monitoring system components:
1. Database connectivity and performance
2. Cache (Redis) status and performance
3. Celery worker status and queue health
4. Overall system health

Each health check returns detailed status information including:
- Component status (healthy/unhealthy)
- Response time metrics
- Error details (if any)
- Last check timestamp
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django_celery_beat.models import PeriodicTask
from django_celery_results.models import TaskResult
from datetime import datetime, timedelta
import time

class HealthCheckView(APIView):
    """
    View for system health check.
    
    This view provides a comprehensive health check of the entire system,
    including database, cache, and Celery worker status.
    
    Returns:
        200 OK: If all components are healthy
        503 Service Unavailable: If any component is unhealthy
        
    Response Format:
    ```json
    {
        "status": "healthy",
        "database": {
            "status": "healthy",
            "database": "postgresql",
            "connection_time": 0.001
        },
        "cache": {
            "status": "healthy",
            "cache_type": "redis",
            "connection_time": 0.001
        },
        "celery": {
            "status": "healthy",
            "worker_count": 2,
            "queue_length": 0,
            "last_heartbeat": "2025-03-27T06:15:42Z"
        }
    }
    """
    
    def get(self, request):
        """
        Get system health status.
        
        This method checks:
        1. Database connectivity
        2. Cache (Redis) connectivity
        3. Celery worker status
        
        Returns:
            Response: Health check response with status information
        """
        # Check database health
        db_health = self._check_database()
        if not db_health['status'] == 'healthy':
            return Response(db_health, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        # Check cache health
        cache_health = self._check_cache()
        if not cache_health['status'] == 'healthy':
            return Response(cache_health, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        # Check Celery health
        celery_health = self._check_celery()
        if not celery_health['status'] == 'healthy':
            return Response(celery_health, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        # Return comprehensive health status
        return Response({
            'status': 'healthy',
            'database': db_health,
            'cache': cache_health,
            'celery': celery_health
        }, status=status.HTTP_200_OK)
    
    def _check_database(self):
        """
        Check database health.
        
        Returns:
            dict: Database health status
        """
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        connection_time = time.time() - start_time
        
        return {
            'status': 'healthy',
            'database': connection.vendor,
            'connection_time': connection_time
        }
    
    def _check_cache(self):
        """
        Check cache health.
        
        Returns:
            dict: Cache health status
        """
        start_time = time.time()
        cache.set('health_check_test', 'test_value', timeout=1)
        value = cache.get('health_check_test')
        connection_time = time.time() - start_time
        
        return {
            'status': 'healthy',
            'cache_type': 'redis',
            'connection_time': connection_time
        }
    
    def _check_celery(self):
        """
        Check Celery health.
        
        Returns:
            dict: Celery health status
        """
        try:
            # Check worker count
            worker_count = len(PeriodicTask.objects.all())
            
            # Check queue length
            queue_length = TaskResult.objects.filter(
                status='PENDING',
                date_created__gt=datetime.now() - timedelta(hours=1)
            ).count()
            
            # Check last heartbeat
            last_heartbeat = TaskResult.objects.filter(
                status='SUCCESS'
            ).order_by('-date_done').first()
            
            return {
                'status': 'healthy',
                'worker_count': worker_count,
                'queue_length': queue_length,
                'last_heartbeat': last_heartbeat.date_done.isoformat() if last_heartbeat else None
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

class DatabaseHealthView(APIView):
    """
    View for database health check.
    
    This view checks the database connection status and response time.
    
    Returns:
        200 OK: If database is healthy
        503 Service Unavailable: If database connection fails
        
    Response Format:
    ```json
    {
        "status": "healthy",
        "database": "postgresql",
        "connection_time": 0.001
    }
    ```
    """
    
    def get(self, request):
        """
        Get database health status.
        
        This method checks:
        1. Database connectivity
        2. Response time
        
        Returns:
            Response: Database health check response
        """
        try:
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection_time = time.time() - start_time
            
            health_data = {
                "status": "healthy",
                "database": connection.vendor,
                "connection_time": connection_time
            }
            
            serializer = DatabaseHealthSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class CacheHealthView(APIView):
    """
    View for cache health check.
    
    This view checks the cache (Redis) connection status and performance.
    
    Returns:
        200 OK: If cache is healthy
        503 Service Unavailable: If cache connection fails
        
    Response Format:
    ```json
    {
        "status": "healthy",
        "cache_type": "redis",
        "connection_time": 0.001
    }
    ```
    """
    
    def get(self, request):
        """
        Get cache health status.
        
        This method checks:
        1. Cache connectivity
        2. Response time
        
        Returns:
            Response: Cache health check response
        """
        try:
            start_time = time.time()
            cache.set('health_check_test', 'test_value', timeout=1)
            value = cache.get('health_check_test')
            connection_time = time.time() - start_time
            
            health_data = {
                "status": "healthy",
                "cache_type": "redis",
                "connection_time": connection_time
            }
            
            serializer = CacheHealthSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class CeleryHealthView(APIView):
    """
    View for Celery health check.
    
    This view checks the Celery worker status and queue length.
    
    Returns:
        200 OK: If Celery is healthy
        503 Service Unavailable: If Celery check fails
        
    Response Format:
    ```json
    {
        "status": "healthy",
        "worker_count": 2,
        "queue_length": 0,
        "last_heartbeat": "2025-03-27T06:15:42Z"
    }
    ```
    """
    
    def get(self, request):
        """
        Get Celery health status.
        
        This method checks:
        1. Worker count
        2. Queue length
        3. Last heartbeat
        
        Returns:
            Response: Celery health check response
        """
        try:
            # Check worker count
            worker_count = len(PeriodicTask.objects.all())
            
            # Check queue length
            queue_length = TaskResult.objects.filter(
                status='PENDING',
                date_created__gt=datetime.now() - timedelta(hours=1)
            ).count()
            
            # Check last heartbeat
            last_heartbeat = TaskResult.objects.filter(
                status='SUCCESS'
            ).order_by('-date_done').first()
            
            health_data = {
                "status": "healthy",
                "worker_count": worker_count,
                "queue_length": queue_length,
                "last_heartbeat": last_heartbeat.date_done.isoformat() if last_heartbeat else None
            }
            
            serializer = CeleryHealthSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
