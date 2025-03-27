"""
Health check views for FinancialMediator.

This module provides health check endpoints for monitoring the application's status.
It includes checks for:
1. Overall system health
2. Database connectivity
3. Cache (Redis) connectivity
4. Celery worker status

The health check endpoints return detailed status information and performance metrics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from redis import Redis
from celery import current_app
from .serializers import HealthCheckSerializer, DatabaseHealthSerializer, CacheHealthSerializer, CeleryHealthSerializer
import time
from datetime import datetime
import os

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
        },
        "timestamp": "2025-03-27T06:15:42Z"
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
        try:
            # Check database health
            start_time = time.time()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_time = time.time() - start_time
            
            database_health = {
                "status": "healthy",
                "database": connection.vendor,
                "connection_time": db_time
            }
            
            # Check cache health
            start_time = time.time()
            redis = Redis.from_url(os.getenv('REDIS_URL'))
            redis.ping()
            cache_time = time.time() - start_time
            
            cache_health = {
                "status": "healthy",
                "cache_type": "redis",
                "connection_time": cache_time
            }
            
            # Check Celery health
            celery_health = {
                "status": "healthy",
                "worker_count": len(current_app.control.ping()),
                "queue_length": len(current_app.control.inspect().active().values()),
                "last_heartbeat": datetime.now()
            }
            
            # Combine all health checks
            health_data = {
                "status": "healthy",
                "database": database_health,
                "cache": cache_health,
                "celery": celery_health,
                "timestamp": datetime.now()
            }
            
            # Serialize and return response
            serializer = HealthCheckSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

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
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class CacheHealthView(APIView):
    """
    View for cache health check.
    
    This view checks the cache (Redis) connection status and response time.
    
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
            redis = Redis.from_url(os.getenv('REDIS_URL'))
            redis.ping()
            connection_time = time.time() - start_time
            
            health_data = {
                "status": "healthy",
                "cache_type": "redis",
                "connection_time": connection_time
            }
            
            serializer = CacheHealthSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now()
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
            health_data = {
                "status": "healthy",
                "worker_count": len(current_app.control.ping()),
                "queue_length": len(current_app.control.inspect().active().values()),
                "last_heartbeat": datetime.now()
            }
            
            serializer = CeleryHealthSerializer(data=health_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now()
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
