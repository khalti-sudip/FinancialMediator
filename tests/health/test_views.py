import pytest
from django.test import TestCase, RequestFactory
from core.health.views import HealthCheckView, DatabaseHealthView, CacheHealthView, CeleryHealthView
from rest_framework.test import force_authenticate
from rest_framework import status
import time
from datetime import datetime

class HealthCheckViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = HealthCheckView.as_view()

    def test_health_check_success(self):
        """Test successful health check response."""
        request = self.factory.get('/health/')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('database', response.data)
        self.assertIn('cache', response.data)
        self.assertIn('celery', response.data)
        self.assertIn('timestamp', response.data)

    def test_health_check_database_failure(self):
        """Test health check response with database failure."""
        request = self.factory.get('/health/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

    def test_health_check_cache_failure(self):
        """Test health check response with cache failure."""
        request = self.factory.get('/health/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

    def test_health_check_celery_failure(self):
        """Test health check response with Celery failure."""
        request = self.factory.get('/health/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

class DatabaseHealthViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = DatabaseHealthView.as_view()

    def test_database_health_success(self):
        """Test successful database health check."""
        request = self.factory.get('/health/db/')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('database', response.data)
        self.assertIn('connection_time', response.data)

    def test_database_health_failure(self):
        """Test database health check with connection failure."""
        request = self.factory.get('/health/db/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

class CacheHealthViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CacheHealthView.as_view()

    def test_cache_health_success(self):
        """Test successful cache health check."""
        request = self.factory.get('/health/cache/')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('cache_type', response.data)
        self.assertIn('connection_time', response.data)

    def test_cache_health_failure(self):
        """Test cache health check with connection failure."""
        request = self.factory.get('/health/cache/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

class CeleryHealthViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = CeleryHealthView.as_view()

    def test_celery_health_success(self):
        """Test successful Celery health check."""
        request = self.factory.get('/health/celery/')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('worker_count', response.data)
        self.assertIn('queue_length', response.data)
        self.assertIn('last_heartbeat', response.data)

    def test_celery_health_failure(self):
        """Test Celery health check with connection failure."""
        request = self.factory.get('/health/celery/')
        with self.assertRaises(Exception):
            response = self.view(request)
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.data)

class HealthCheckMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_health_check_middleware(self):
        """Test health check middleware."""
        request = self.factory.get('/health/')
        response = self.client.get('/health/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.json())
        self.assertIn('database', response.json())
        self.assertIn('cache', response.json())
        self.assertIn('celery', response.json())
        self.assertIn('timestamp', response.json())

    def test_health_check_middleware_failure(self):
        """Test health check middleware with service failure."""
        request = self.factory.get('/health/')
        with self.assertRaises(Exception):
            response = self.client.get('/health/')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.json())

    def test_health_check_middleware_database_failure(self):
        """Test health check middleware with database failure."""
        request = self.factory.get('/health/db/')
        with self.assertRaises(Exception):
            response = self.client.get('/health/db/')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.json())

    def test_health_check_middleware_cache_failure(self):
        """Test health check middleware with cache failure."""
        request = self.factory.get('/health/cache/')
        with self.assertRaises(Exception):
            response = self.client.get('/health/cache/')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.json())

    def test_health_check_middleware_celery_failure(self):
        """Test health check middleware with Celery failure."""
        request = self.factory.get('/health/celery/')
        with self.assertRaises(Exception):
            response = self.client.get('/health/celery/')
            self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
            self.assertIn('error', response.json())

    def test_health_check_middleware_invalid_path(self):
        """Test health check middleware with invalid path."""
        request = self.factory.get('/health/invalid/')
        response = self.client.get('/health/invalid/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
