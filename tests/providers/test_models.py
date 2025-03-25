"""
Provider Models Test Module.

This module tests:
- Provider model
- API key model
- Webhook model
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from providers.models import Provider, ProviderKey, ProviderWebhook

User = get_user_model()

class ProviderModelTest(TestCase):
    """Test cases for Provider model."""
    
    def setUp(self):
        """Set up test data."""
        self.provider_data = {
            "name": "Test Provider",
            "code": "TEST",
            "provider_type": "payment",
            "supported_currencies": ["USD", "EUR"],
            "supported_countries": ["US", "GB"],
            "api_base_url": "https://api.test.com",
            "api_version": "v1",
            "webhook_url": "https://webhook.test.com",
            "rate_limit": 1000,
            "concurrent_requests": 10,
            "settings": {
                "success_url": "https://success.test.com",
                "cancel_url": "https://cancel.test.com",
                "webhook_events": ["payment.success", "payment.failure"],
            },
        }
        
        self.provider = Provider.objects.create(**self.provider_data)
    
    def test_create_provider(self):
        """Test provider creation."""
        self.assertEqual(self.provider.name, "Test Provider")
        self.assertEqual(self.provider.code, "TEST")
        self.assertTrue(self.provider.is_active)
        self.assertEqual(self.provider.status, "active")
    
    def test_provider_str(self):
        """Test provider string representation."""
        self.assertEqual(
            str(self.provider),
            "Test Provider (TEST)"
        )
    
    def test_invalid_code(self):
        """Test invalid provider code."""
        self.provider_data["code"] = "test@123"
        
        with self.assertRaises(ValidationError):
            Provider.objects.create(**self.provider_data)
    
    def test_invalid_settings(self):
        """Test invalid provider settings."""
        self.provider_data["settings"] = {}
        
        with self.assertRaises(ValidationError):
            Provider.objects.create(**self.provider_data)
    
    def test_check_status(self):
        """Test provider status check."""
        is_healthy = self.provider.check_status()
        self.assertTrue(is_healthy)
        self.assertIsNotNone(self.provider.last_check_at)

class ProviderKeyModelTest(TestCase):
    """Test cases for ProviderKey model."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        
        self.key_data = {
            "provider": self.provider,
            "user": self.user,
            "environment": "test",
            "daily_limit": 1000,
            "monthly_limit": 30000,
            "key_data": {
                "key_id": "test_key",
                "key_secret": "test_secret",
            },
        }
        
        self.key = ProviderKey.objects.create(**self.key_data)
    
    def test_create_key(self):
        """Test API key creation."""
        self.assertEqual(self.key.provider, self.provider)
        self.assertEqual(self.key.user, self.user)
        self.assertTrue(self.key.is_active)
    
    def test_key_str(self):
        """Test key string representation."""
        self.assertEqual(
            str(self.key),
            f"API Key: {self.key.key_id} ({self.provider.code})"
        )
    
    def test_duplicate_key(self):
        """Test duplicate API key creation."""
        with self.assertRaises(ValidationError):
            ProviderKey.objects.create(**self.key_data)
    
    def test_invalid_limits(self):
        """Test invalid usage limits."""
        self.key_data["monthly_limit"] = 100
        
        with self.assertRaises(ValidationError):
            ProviderKey.objects.create(**self.key_data)
    
    def test_usage_tracking(self):
        """Test usage tracking."""
        self.key.track_usage(50)
        self.assertEqual(self.key.daily_usage, 50)
        self.assertEqual(self.key.monthly_usage, 50)
        self.assertIsNotNone(self.key.last_used_at)

class ProviderWebhookModelTest(TestCase):
    """Test cases for ProviderWebhook model."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
            webhook_secret="test_secret",
        )
        
        self.webhook_data = {
            "provider": self.provider,
            "event_type": "payment.success",
            "event_data": {
                "transaction_id": "test_tx",
                "amount": 100,
                "currency": "USD",
            },
            "signature": "test_signature",
            "ip_address": "127.0.0.1",
            "headers": {
                "User-Agent": "Test",
            },
        }
        
        self.webhook = ProviderWebhook.objects.create(
            **self.webhook_data
        )
    
    def test_create_webhook(self):
        """Test webhook creation."""
        self.assertEqual(self.webhook.provider, self.provider)
        self.assertEqual(self.webhook.status, "pending")
        self.assertEqual(self.webhook.retry_count, 0)
    
    def test_webhook_str(self):
        """Test webhook string representation."""
        self.assertEqual(
            str(self.webhook),
            f"Webhook: {self.webhook.event_id} ({self.provider.code})"
        )
    
    def test_process_webhook(self):
        """Test webhook processing."""
        self.webhook.process()
        self.assertEqual(self.webhook.status, "completed")
        self.assertIsNotNone(self.webhook.processed_at)
    
    def test_retry_webhook(self):
        """Test webhook retry."""
        self.webhook.status = "failed"
        self.webhook.save()
        
        self.webhook.retry()
        self.assertEqual(self.webhook.status, "pending")
        self.assertEqual(self.webhook.retry_count, 1)
    
    def test_max_retries(self):
        """Test maximum retries."""
        self.webhook.retry_count = 3
        self.webhook.save()
        
        with self.assertRaises(ValidationError):
            self.webhook.retry()
