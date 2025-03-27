import pytest
from django.test import TestCase, RequestFactory
from django.core.cache import cache
from rest_framework import status
from core.middleware.rate_limit import RateLimitMiddleware, rate_limit, RateLimitException, RateLimitConfig
from datetime import datetime
from typing import Callable

class RateLimitMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RateLimitMiddleware(lambda x: x)
        cache.clear()

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded response."""
        request = self.factory.get('/')
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_127.0.0.1', 100, 60)
        
        response = self.middleware.process_request(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

    def test_rate_limit_not_exceeded(self):
        """Test rate limit not exceeded response."""
        request = self.factory.get('/')
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)

    def test_get_client_ip(self):
        """Test getting client IP address."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

    def test_get_client_ip_x_forwarded_for(self):
        """Test getting client IP address from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 127.0.0.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

class RateLimitDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def test_rate_limit_decorator(self):
        """Test rate limit decorator."""
        @rate_limit(requests_per_minute=10, window_seconds=60)
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        
        # First request should succeed
        response = test_view(request)
        self.assertTrue(response['success'])
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_test_view_127.0.0.1', 10, 60)
        
        # Second request should fail
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

    def test_rate_limit_decorator_custom_key(self):
        """Test rate limit decorator with custom key."""
        @rate_limit(requests_per_minute=10, window_seconds=60, key='custom_key')
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        
        # First request should succeed
        response = test_view(request)
        self.assertTrue(response['success'])
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_custom_key_127.0.0.1', 10, 60)
        
        # Second request should fail
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

class RateLimitExceptionTest(TestCase):
    def test_rate_limit_exception(self):
        """Test rate limit exception."""
        exception = RateLimitException(
            'Rate limit exceeded',
            limit=100,
            window=60
        )
        
        self.assertEqual(str(exception), 'Rate limit exceeded')
        self.assertEqual(exception.limit, 100)
        self.assertEqual(exception.window, 60)

class RateLimitConfigTest(TestCase):
    def test_rate_limit_config(self):
        """Test rate limit configuration."""
        config = RateLimitConfig(
            requests_per_minute=100,
            window_seconds=60,
            key='custom_key'
        )
        
        @config
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        
        # First request should succeed
        response = test_view(request)
        self.assertTrue(response['success'])
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_custom_key_127.0.0.1', 100, 60)
        
        # Second request should fail
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

class RateLimitMiddlewareIntegrationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    def test_rate_limit_middleware_integration(self):
        """Test rate limit middleware integration."""
        @rate_limit(requests_per_minute=10, window_seconds=60)
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        
        # First request should succeed
        response = test_view(request)
        self.assertTrue(response['success'])
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_test_view_127.0.0.1', 10, 60)
        
        # Second request should fail
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

    def test_rate_limit_middleware_integration_custom_key(self):
        """Test rate limit middleware integration with custom key."""
        @rate_limit(requests_per_minute=10, window_seconds=60, key='custom_key')
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        
        # First request should succeed
        response = test_view(request)
        self.assertTrue(response['success'])
        
        # Set up cache with rate limit exceeded
        cache.set('rate_limit_custom_key_127.0.0.1', 10, 60)
        
        # Second request should fail
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('error', response.json())
        self.assertIn('limit', response.json())
        self.assertIn('window', response.json())

    def test_rate_limit_middleware_integration_exception(self):
        """Test rate limit middleware integration with exception."""
        @rate_limit(requests_per_minute=10, window_seconds=60)
        def test_view(request):
            raise Exception('Test exception')

        request = self.factory.get('/')
        
        with self.assertRaises(Exception):
            response = test_view(request)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.json())

    def test_rate_limit_middleware_integration_invalid_request(self):
        """Test rate limit middleware integration with invalid request."""
        @rate_limit(requests_per_minute=10, window_seconds=60)
        def test_view(request):
            return {'success': True}

        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = None
        
        response = test_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
