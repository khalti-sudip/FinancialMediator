from rest_framework import serializers
from django.db import connection
from redis import Redis
from celery import current_app

class DatabaseHealthSerializer(serializers.Serializer):
    """Serializer for database health status."""
    status = serializers.CharField()
    database = serializers.CharField()
    connection_time = serializers.FloatField()

class CacheHealthSerializer(serializers.Serializer):
    """Serializer for cache health status."""
    status = serializers.CharField()
    cache_type = serializers.CharField()
    connection_time = serializers.FloatField()

class CeleryHealthSerializer(serializers.Serializer):
    """Serializer for Celery health status."""
    status = serializers.CharField()
    worker_count = serializers.IntegerField()
    queue_length = serializers.IntegerField()
    last_heartbeat = serializers.DateTimeField()

class HealthCheckSerializer(serializers.Serializer):
    """Serializer for overall health check status."""
    status = serializers.CharField()
    database = DatabaseHealthSerializer()
    cache = CacheHealthSerializer()
    celery = CeleryHealthSerializer()
    timestamp = serializers.DateTimeField()
