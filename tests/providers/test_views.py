"""
Provider Views Test Module.

This module tests:
- Provider viewset
- API key viewset
- Webhook viewset
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from providers.models import Provider, ProviderKey, ProviderWebhook

User = get_user_model()

class ProviderViewSetTest(TestCase):
    """Test cases for Provider viewset."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test provider
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
            supported_currencies=["USD", "EUR"],
            supported_countries=["US", "GB"],
            api_base_url="https://api.test.com",
            settings={
                "success_url": "https://success.test.com",
                "cancel_url": "https://cancel.test.com",
                "webhook_events": ["payment.success"],
            },
        )
    
    def test_list_providers(self):
        """Test listing providers."""
        url = reverse("provider-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_provider(self):
        """Test creating provider."""
        url = reverse("provider-list")
        data = {
            "name": "New Provider",
            "code": "NEW",
            "provider_type": "wallet",
            "supported_currencies": ["USD"],
            "supported_countries": ["US"],
            "api_base_url": "https://api.new.com",
            "settings": {
                "balance_check_interval": 300,
                "auto_refund": True,
            },
        }
        
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_check_status(self):
        """Test checking provider status."""
        url = reverse("provider-check-status", args=[self.provider.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_healthy", response.data)
    
    def test_update_status(self):
        """Test updating provider status."""
        url = reverse("provider-update-status", args=[self.provider.id])
        data = {
            "status": "maintenance",
            "message": "Scheduled maintenance",
        }
        
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.provider.refresh_from_db()
        self.assertEqual(self.provider.status, "maintenance")
    
    def test_get_statistics(self):
        """Test getting provider statistics."""
        url = reverse("provider-statistics", args=[self.provider.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_requests", response.data)

class ProviderKeyViewSetTest(TestCase):
    """Test cases for ProviderKey viewset."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test provider
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
        )
        
        # Create test key
        self.key = ProviderKey.objects.create(
            provider=self.provider,
            user=self.user,
            environment="test",
            daily_limit=1000,
            monthly_limit=30000,
            key_data={"key_id": "test_key"},
        )
    
    def test_list_keys(self):
        """Test listing API keys."""
        url = reverse("provider-key-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_key(self):
        """Test creating API key."""
        url = reverse("provider-key-list")
        data = {
            "provider": self.provider.id,
            "user": self.user.id,
            "environment": "prod",
            "daily_limit": 5000,
            "monthly_limit": 150000,
        }
        
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_deactivate_key(self):
        """Test deactivating API key."""
        url = reverse("provider-key-deactivate", args=[self.key.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.key.refresh_from_db()
        self.assertFalse(self.key.is_active)
    
    def test_get_usage(self):
        """Test getting key usage."""
        url = reverse("provider-key-usage", args=[self.key.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("daily_usage", response.data)

class ProviderWebhookViewSetTest(TestCase):
    """Test cases for ProviderWebhook viewset."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test provider
        self.provider = Provider.objects.create(
            name="Test Provider",
            code="TEST",
            provider_type="payment",
            webhook_secret="test_secret",
        )
        
        # Create test webhook
        self.webhook = ProviderWebhook.objects.create(
            provider=self.provider,
            event_type="payment.success",
            event_data={
                "transaction_id": "test_tx",
                "amount": 100,
            },
            signature="test_signature",
            ip_address="127.0.0.1",
        )
    
    def test_list_webhooks(self):
        """Test listing webhooks."""
        url = reverse("provider-webhook-list")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_webhook(self):
        """Test creating webhook."""
        url = reverse("provider-webhook-list")
        data = {
            "provider": self.provider.id,
            "event_type": "payment.refund",
            "event_data": {
                "refund_id": "test_refund",
                "amount": 50,
            },
            "signature": "new_signature",
            "ip_address": "127.0.0.1",
        }
        
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_retry_webhook(self):
        """Test retrying webhook."""
        self.webhook.status = "failed"
        self.webhook.save()
        
        url = reverse("provider-webhook-retry", args=[self.webhook.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.webhook.refresh_from_db()
        self.assertEqual(self.webhook.status, "pending")
    
    def test_cancel_webhook(self):
        """Test cancelling webhook."""
        url = reverse("provider-webhook-cancel", args=[self.webhook.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.webhook.refresh_from_db()
        self.assertEqual(self.webhook.status, "cancelled")
    
    def test_get_summary(self):
        """Test getting webhook summary."""
        url = reverse("provider-webhook-summary")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total", response.data)
        self.assertIn("success_rate", response.data)
