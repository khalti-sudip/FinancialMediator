"""
Provider Serializers Test Module.

This module tests:
- Provider serializer
- API key serializer
- Webhook serializer
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from providers.models import Provider, ProviderKey, ProviderWebhook
from providers.serializers import (
    ProviderSerializer,
    ProviderKeySerializer,
    ProviderWebhookSerializer,
    ProviderStatusSerializer,
    ProviderStatsSerializer,
)

User = get_user_model()

class ProviderSerializerTest(TestCase):
    """Test cases for Provider serializer."""
    
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
        
        self.serializer = ProviderSerializer(data=self.provider_data)
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_code(self):
        """Test serializer with invalid code."""
        self.provider_data["code"] = "test@123"
        serializer = ProviderSerializer(data=self.provider_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
    
    def test_missing_settings(self):
        """Test serializer with missing settings."""
        self.provider_data["settings"] = {}
        serializer = ProviderSerializer(data=self.provider_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        self.provider_data["created_at"] = timezone.now()
        serializer = ProviderSerializer(data=self.provider_data)
        
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("created_at", serializer.validated_data)

class ProviderKeySerializerTest(TestCase):
    """Test cases for ProviderKey serializer."""
    
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
            "provider": self.provider.id,
            "user": self.user.id,
            "environment": "test",
            "daily_limit": 1000,
            "monthly_limit": 30000,
            "key_data": {
                "key_id": "test_key",
                "key_secret": "test_secret",
            },
        }
        
        self.serializer = ProviderKeySerializer(data=self.key_data)
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_limits(self):
        """Test serializer with invalid limits."""
        self.key_data["monthly_limit"] = 100
        serializer = ProviderKeySerializer(data=self.key_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
    
    def test_duplicate_key(self):
        """Test serializer with duplicate key."""
        ProviderKey.objects.create(
            provider=self.provider,
            user=self.user,
            environment="test",
            key_data={"key_id": "old_key"},
        )
        
        with self.assertRaises(ValidationError):
            self.serializer.is_valid(raise_exception=True)

class ProviderWebhookSerializerTest(TestCase):
    """Test cases for ProviderWebhook serializer."""
    
    def setUp(self):
        """Set up test data."""
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
            webhook_secret="test_secret",
        )
        
        self.webhook_data = {
            "provider": self.provider.id,
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
        
        self.serializer = ProviderWebhookSerializer(data=self.webhook_data)
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_signature(self):
        """Test serializer with invalid signature."""
        from providers.utils import calculate_signature
        
        # Calculate correct signature
        correct_sig = calculate_signature(
            self.webhook_data["event_data"],
            self.provider.webhook_secret,
        )
        
        # Use wrong signature
        self.webhook_data["signature"] = "wrong_signature"
        serializer = ProviderWebhookSerializer(data=self.webhook_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
    
    def test_read_only_fields(self):
        """Test read-only fields."""
        self.webhook_data["status"] = "completed"
        self.webhook_data["processed_at"] = timezone.now()
        
        self.assertTrue(self.serializer.is_valid())
        self.assertNotIn("status", self.serializer.validated_data)
        self.assertNotIn("processed_at", self.serializer.validated_data)

class ProviderStatusSerializerTest(TestCase):
    """Test cases for ProviderStatus serializer."""
    
    def setUp(self):
        """Set up test data."""
        self.status_data = {
            "status": "active",
            "message": "Provider is healthy",
            "metadata": {
                "response_time": 100,
                "error_rate": 0.01,
            },
        }
        
        self.serializer = ProviderStatusSerializer(data=self.status_data)
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_status(self):
        """Test serializer with invalid status."""
        self.status_data["status"] = "unknown"
        serializer = ProviderStatusSerializer(data=self.status_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

class ProviderStatsSerializerTest(TestCase):
    """Test cases for ProviderStats serializer."""
    
    def setUp(self):
        """Set up test data."""
        self.stats_data = {
            "total_requests": 1000,
            "success_rate": 0.99,
            "average_response_time": 150.5,
            "error_rate": 0.01,
            "active_keys": 5,
            "webhook_success_rate": 0.98,
            "last_update": timezone.now().isoformat(),
        }
        
        self.serializer = ProviderStatsSerializer(data=self.stats_data)
    
    def test_valid_data(self):
        """Test serializer with valid data."""
        self.assertTrue(self.serializer.is_valid())
    
    def test_invalid_rates(self):
        """Test serializer with invalid rates."""
        self.stats_data["success_rate"] = 1.5
        serializer = ProviderStatsSerializer(data=self.stats_data)
        
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
