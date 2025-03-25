"""
Health Check Serializers Module.

This module provides serializers for:
- System health status
- Database connectivity
- Redis connectivity
- Celery worker status
"""

from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for system health checks."""
    
    status = serializers.CharField(help_text="Overall system status")
    timestamp = serializers.DateTimeField(help_text="Time of the health check")
    
    # Components
    components = serializers.DictField(
        help_text="Status of individual system components",
        child=serializers.DictField()
    )
    
    # System info
    version = serializers.CharField(help_text="API version")
    environment = serializers.CharField(help_text="Environment (development, staging, production)")


class DatabaseHealthSerializer(serializers.Serializer):
    """Serializer for database health checks."""
    
    status = serializers.CharField(help_text="Database connection status")
    latency_ms = serializers.FloatField(help_text="Query latency in milliseconds")
    connection_pool = serializers.DictField(help_text="Database connection pool stats")
    database_name = serializers.CharField(help_text="Connected database name")


class RedisHealthSerializer(serializers.Serializer):
    """Serializer for Redis health checks."""
    
    status = serializers.CharField(help_text="Redis connection status")
    latency_ms = serializers.FloatField(help_text="Command latency in milliseconds")
    used_memory = serializers.CharField(help_text="Memory used by Redis")
    clients_connected = serializers.IntegerField(help_text="Number of connected clients")


class CeleryHealthSerializer(serializers.Serializer):
    """Serializer for Celery health checks."""
    
    status = serializers.CharField(help_text="Celery worker status")
    workers = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of active workers"
    )
    queues = serializers.DictField(help_text="Queue status")
    tasks_processed = serializers.IntegerField(help_text="Number of tasks processed")
