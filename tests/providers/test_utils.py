"""
Provider Utils Test Module.

This module tests:
- Signature verification
- Key generation
- Credential management
- Webhook handling
"""

from django.test import TestCase
from django.utils import timezone
from providers.utils import (
    calculate_signature,
    verify_signature,
    generate_api_key,
    generate_provider_credentials,
    get_webhook_handler,
    get_notification_service,
)

class SignatureUtilsTest(TestCase):
    """Test cases for signature utilities."""
    
    def setUp(self):
        """Set up test data."""
        self.test_data = {
            "event": "payment.success",
            "amount": 100,
            "currency": "USD",
            "timestamp": timezone.now().isoformat(),
        }
        self.test_secret = "test_webhook_secret"
    
    def test_calculate_signature(self):
        """Test signature calculation."""
        signature = calculate_signature(self.test_data, self.test_secret)
        
        self.assertIsNotNone(signature)
        self.assertTrue(isinstance(signature, str))
        self.assertEqual(len(signature), 64)  # SHA256 hex digest
    
    def test_verify_signature(self):
        """Test signature verification."""
        # Calculate signature
        signature = calculate_signature(self.test_data, self.test_secret)
        
        # Verify correct signature
        self.assertTrue(
            verify_signature(self.test_data, signature, self.test_secret)
        )
        
        # Verify wrong signature
        self.assertFalse(
            verify_signature(
                self.test_data,
                "wrong_signature",
                self.test_secret
            )
        )
    
    def test_data_tampering(self):
        """Test signature with tampered data."""
        # Calculate signature
        signature = calculate_signature(self.test_data, self.test_secret)
        
        # Modify data
        tampered_data = self.test_data.copy()
        tampered_data["amount"] = 200
        
        # Verify signature with tampered data
        self.assertFalse(
            verify_signature(tampered_data, signature, self.test_secret)
        )

class KeyGenerationTest(TestCase):
    """Test cases for key generation."""
    
    def test_generate_api_key(self):
        """Test API key generation."""
        key_pair = generate_api_key()
        
        self.assertIn("key_id", key_pair)
        self.assertIn("key_secret", key_pair)
        
        # Check key_id format
        self.assertEqual(len(key_pair["key_id"]), 16)
        self.assertTrue(key_pair["key_id"].isalnum())
        
        # Check key_secret format
        self.assertEqual(len(key_pair["key_secret"]), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in key_pair["key_secret"]))
    
    def test_unique_keys(self):
        """Test key uniqueness."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        self.assertNotEqual(key1["key_id"], key2["key_id"])
        self.assertNotEqual(key1["key_secret"], key2["key_secret"])
    
    def test_custom_length(self):
        """Test custom key length."""
        key_pair = generate_api_key(length=16)
        self.assertEqual(len(key_pair["key_secret"]), 32)

class CredentialGenerationTest(TestCase):
    """Test cases for credential generation."""
    
    def test_payment_credentials(self):
        """Test payment provider credentials."""
        creds = generate_provider_credentials("payment")
        
        self.assertIn("api_key", creds)
        self.assertIn("api_secret", creds)
        self.assertIn("merchant_id", creds)
        self.assertTrue(creds["merchant_id"].startswith("MERCH_"))
    
    def test_wallet_credentials(self):
        """Test wallet provider credentials."""
        creds = generate_provider_credentials("wallet")
        
        self.assertIn("wallet_id", creds)
        self.assertIn("access_key", creds)
        self.assertIn("secret_key", creds)
        self.assertTrue(creds["wallet_id"].startswith("WALL_"))
    
    def test_bank_credentials(self):
        """Test bank provider credentials."""
        creds = generate_provider_credentials("bank")
        
        self.assertIn("client_id", creds)
        self.assertIn("client_secret", creds)
        self.assertIn("access_token", creds)
        self.assertTrue(creds["client_id"].startswith("BANK_"))
    
    def test_kyc_credentials(self):
        """Test KYC provider credentials."""
        creds = generate_provider_credentials("kyc")
        
        self.assertIn("partner_id", creds)
        self.assertIn("api_key", creds)
        self.assertIn("webhook_secret", creds)
        self.assertTrue(creds["partner_id"].startswith("KYC_"))
    
    def test_invalid_provider(self):
        """Test invalid provider type."""
        with self.assertRaises(ValueError):
            generate_provider_credentials("invalid")

class WebhookHandlerTest(TestCase):
    """Test cases for webhook handlers."""
    
    def setUp(self):
        """Set up test data."""
        self.payment_data = {
            "transaction_id": "test_tx",
            "amount": 100,
            "currency": "USD",
        }
        
        self.wallet_data = {
            "wallet_id": "test_wallet",
            "amount": 50,
            "currency": "EUR",
        }
    
    def test_payment_handler(self):
        """Test payment webhook handler."""
        handler = get_webhook_handler("payment", "payment.success")
        
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))
        self.assertTrue(handler(self.payment_data))
    
    def test_wallet_handler(self):
        """Test wallet webhook handler."""
        handler = get_webhook_handler("wallet", "wallet.deposit")
        
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))
        self.assertTrue(handler(self.wallet_data))
    
    def test_default_handler(self):
        """Test default webhook handler."""
        handler = get_webhook_handler("payment", "unknown.event")
        
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))
    
    def test_invalid_handler(self):
        """Test invalid webhook handler."""
        handler = get_webhook_handler("invalid", "test.event")
        self.assertIsNone(handler)

class NotificationServiceTest(TestCase):
    """Test cases for notification service."""
    
    def test_get_service(self):
        """Test getting notification service."""
        service = get_notification_service()
        
        self.assertIsNotNone(service)
        self.assertTrue(hasattr(service, "send_alert"))
    
    def test_service_config(self):
        """Test service configuration."""
        with self.settings(NOTIFICATION_SERVICE={"test": "value"}):
            service = get_notification_service()
            self.assertEqual(service.test, "value")
