from django.test import TestCase
from django.utils import timezone
from banking_api.models import User, ApiKey, Transaction
import uuid

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            balance=1000,
            daily_transaction_limit=5000
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.balance, 1000)
        self.assertEqual(self.user.daily_transaction_limit, 5000)

    def test_soft_deletion(self):
        self.assertFalse(self.user.is_deleted)
        self.assertIsNone(self.user.deleted_at)
        
        self.user.delete()
        self.assertTrue(self.user.is_deleted)
        self.assertIsNotNone(self.user.deleted_at)

    def test_balance_validation(self):
        self.assertTrue(self.user.has_sufficient_balance(500))
        self.assertFalse(self.user.has_sufficient_balance(1500))

    def test_transaction_limit(self):
        self.assertTrue(self.user.can_perform_transaction(1000))
        self.assertFalse(self.user.can_perform_transaction(6000))

class ApiKeyModelTest(TestCase):
    def setUp(self):
        self.api_key = ApiKey.objects.create(
            key='test-key-123',
            name='Test API Key',
            rate_limit=100,
            ip_whitelist=['192.168.1.1'],
            allowed_methods=['GET', 'POST']
        )

    def test_api_key_creation(self):
        self.assertEqual(self.api_key.name, 'Test API Key')
        self.assertEqual(self.api_key.rate_limit, 100)
        self.assertEqual(self.api_key.ip_whitelist, ['192.168.1.1'])

    def test_rate_limit_validation(self):
        self.assertTrue(self.api_key.is_valid())
        
        self.api_key.rate_limit = 0
        self.assertFalse(self.api_key.is_valid())

    def test_ip_whitelist(self):
        self.assertTrue(self.api_key.is_valid())
        
        self.api_key.ip_whitelist = ['10.0.0.1']
        self.assertFalse(self.api_key.is_valid())

class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='test@example.com',
            balance=1000
        )
        self.transaction = Transaction.objects.create(
            transaction_id=str(uuid.uuid4()),
            source_system='test-system',
            target_system='bank-system',
            transaction_type='deposit',
            status='pending',
            amount=500,
            currency='USD',
            user=self.user,
            request_data={'amount': 500}
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.status, 'pending')
        self.assertEqual(self.transaction.amount, 500)
        self.assertEqual(self.transaction.currency, 'USD')

    def test_amount_validation(self):
        self.assertTrue(self.transaction.amount > 0)
        
        self.transaction.amount = -100
        self.assertFalse(self.transaction.amount > 0)

    def test_status_updates(self):
        self.assertEqual(self.transaction.status, 'pending')
        
        self.transaction.update_status('completed')
        self.assertEqual(self.transaction.status, 'completed')
        
        self.transaction.update_status('failed')
        self.assertEqual(self.transaction.status, 'failed')
