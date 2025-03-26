from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django_redis import get_redis_connection
from celery import current_app
from datetime import datetime
from .serializers import HealthStatusSerializer

class HealthCheckView(APIView):
    """API view for system health monitoring."""
    
    def get(self, request):
        """Check system health status."""
        health_data = {
            'timestamp': datetime.now(),
            'database': self.check_database(),
            'redis': self.check_redis(),
            'celery': self.check_celery()
        }
        
        serializer = HealthStatusSerializer(health_data)
        return Response(serializer.data)
    
    def check_database(self):
        """Check database health."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
    
    def check_redis(self):
        """Check Redis health."""
        try:
            redis = get_redis_connection()
            redis.ping()
            return {
                'status': 'healthy',
                'message': 'Redis connection successful'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Redis connection failed: {str(e)}'
            }
    
    def check_celery(self):
        """Check Celery health."""
        try:
            stats = current_app.control.inspect().stats()
            if stats:
                return {
                    'status': 'healthy',
                    'message': 'Celery workers active',
                    'workers': len(stats)
                }
            return {
                'status': 'warning',
                'message': 'No active Celery workers found'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Celery check failed: {str(e)}'
            }
