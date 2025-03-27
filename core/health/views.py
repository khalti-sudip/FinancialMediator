from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from redis import Redis
from celery import current_app
from .serializers import HealthCheckSerializer, DatabaseHealthSerializer, CacheHealthSerializer, CeleryHealthSerializer
import time
from datetime import datetime

class HealthCheckView(APIView):
    """View for system health check."""
    
    def get(self, request):
        """Get system health status."""
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
    """View for database health check."""
    
    def get(self, request):
        """Get database health status."""
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
    """View for cache health check."""
    
    def get(self, request):
        """Get cache health status."""
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
    """View for Celery health check."""
    
    def get(self, request):
        """Get Celery health status."""
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
