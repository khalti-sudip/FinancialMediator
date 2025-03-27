"""
Health check serializers for FinancialMediator.

This module provides serializers for health check responses, including:
1. Database health status
2. Cache health status
3. Celery health status
4. Overall system health status

The serializers ensure consistent response formats and proper validation of health check data.
"""

from rest_framework import serializers
from django.db import connection
from redis import Redis
from celery import current_app
import time
from datetime import datetime

class DatabaseHealthSerializer(serializers.Serializer):
    """
    Serializer for database health status.
    
    This serializer validates and formats database health check responses.
    
    Fields:
    - status: Health status ("healthy" or "unhealthy")
    - database: Database type (e.g., "postgresql", "sqlite")
    - connection_time: Time taken to establish connection (in seconds)
    """
    status = serializers.CharField()
    database = serializers.CharField()
    connection_time = serializers.FloatField()

class CacheHealthSerializer(serializers.Serializer):
    """
    Serializer for cache health status.
    
    This serializer validates and formats cache health check responses.
    
    Fields:
    - status: Health status ("healthy" or "unhealthy")
    - cache_type: Cache type (e.g., "redis", "memcached")
    - connection_time: Time taken to establish connection (in seconds)
    """
    status = serializers.CharField()
    cache_type = serializers.CharField()
    connection_time = serializers.FloatField()

class CeleryHealthSerializer(serializers.Serializer):
    """
    Serializer for Celery health status.
    
    This serializer validates and formats Celery health check responses.
    
    Fields:
    - status: Health status ("healthy" or "unhealthy")
    - worker_count: Number of active Celery workers
    - queue_length: Number of tasks in the queue
    - last_heartbeat: Timestamp of the last worker heartbeat
    """
    status = serializers.CharField()
    worker_count = serializers.IntegerField()
    queue_length = serializers.IntegerField()
    last_heartbeat = serializers.DateTimeField()

class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for overall health check status.
    
    This serializer validates and formats comprehensive health check responses,
    combining data from database, cache, and Celery health checks.
    
    Fields:
    - status: Overall health status ("healthy" or "unhealthy")
    - database: Database health status (nested DatabaseHealthSerializer)
    - cache: Cache health status (nested CacheHealthSerializer)
    - celery: Celery health status (nested CeleryHealthSerializer)
    - timestamp: Timestamp of the health check
    """
    status = serializers.CharField()
    database = DatabaseHealthSerializer()
    cache = CacheHealthSerializer()
    celery = CeleryHealthSerializer()
    timestamp = serializers.DateTimeField()
