import os
import sys
import django
from django.test import TestCase
from banking_api.models import User, ApiKey, Transaction
import uuid

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

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
