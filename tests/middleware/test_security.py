import pytest
from django.test import TestCase, RequestFactory
from core.middleware.security import SecurityHeadersMiddleware

class SecurityHeadersMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = SecurityHeadersMiddleware()

    def test_security_headers(self):
        """Test that all security headers are properly set."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, self.client.get('/').wsgi_response)

        # Test Content Security Policy
        self.assertIn('Content-Security-Policy', response)
        self.assertIn('default-src', response['Content-Security-Policy'])

        # Test X-Content-Type-Options
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

        # Test X-Frame-Options
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')

        # Test X-XSS-Protection
        self.assertIn('X-XSS-Protection', response)
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

        # Test Strict-Transport-Security
        self.assertIn('Strict-Transport-Security', response)
        self.assertEqual(response['Strict-Transport-Security'], 'max-age=31536000; includeSubDomains; preload')

        # Test X-Permitted-Cross-Domain-Policies
        self.assertIn('X-Permitted-Cross-Domain-Policies', response)
        self.assertEqual(response['X-Permitted-Cross-Domain-Policies'], 'none')

        # Test Referrer-Policy
        self.assertIn('Referrer-Policy', response)
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')

        # Test Feature-Policy
        self.assertIn('Feature-Policy', response)
        self.assertIn('geolocation', response['Feature-Policy'])
        self.assertIn('microphone', response['Feature-Policy'])
        self.assertIn('camera', response['Feature-Policy'])

    def test_headers_not_modified(self):
        """Test that existing headers are not modified."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, self.client.get('/').wsgi_response)
        
        # Add a custom header
        response['X-Custom-Header'] = 'test-value'
        
        # Process response again
        processed_response = self.middleware.process_response(request, response)
        
        # Verify custom header is preserved
        self.assertIn('X-Custom-Header', processed_response)
        self.assertEqual(processed_response['X-Custom-Header'], 'test-value')

    def test_headers_not_removed(self):
        """Test that other headers are not removed."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, self.client.get('/').wsgi_response)
        
        # Add a custom header
        response['X-Custom-Header'] = 'test-value'
        
        # Process response again
        processed_response = self.middleware.process_response(request, response)
        
        # Verify custom header is still present
        self.assertIn('X-Custom-Header', processed_response)
        self.assertEqual(processed_response['X-Custom-Header'], 'test-value')

    def test_headers_not_modified_on_error(self):
        """Test that headers are not modified on error responses."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, self.client.get('/').wsgi_response)
        
        # Set status code to error
        response.status_code = 500
        
        # Process response
        processed_response = self.middleware.process_response(request, response)
        
        # Verify headers are still present
        self.assertIn('Content-Security-Policy', processed_response)
        self.assertIn('X-Content-Type-Options', processed_response)
        self.assertIn('X-Frame-Options', processed_response)
        self.assertIn('X-XSS-Protection', processed_response)
        self.assertIn('Strict-Transport-Security', processed_response)

    def test_headers_not_modified_on_redirect(self):
        """Test that headers are not modified on redirect responses."""
        request = self.factory.get('/')
        response = self.middleware.process_response(request, self.client.get('/').wsgi_response)
        
        # Set status code to redirect
        response.status_code = 302
        
        # Process response
        processed_response = self.middleware.process_response(request, response)
        
        # Verify headers are still present
        self.assertIn('Content-Security-Policy', processed_response)
        self.assertIn('X-Content-Type-Options', processed_response)
        self.assertIn('X-Frame-Options', processed_response)
        self.assertIn('X-XSS-Protection', processed_response)
        self.assertIn('Strict-Transport-Security', processed_response)
