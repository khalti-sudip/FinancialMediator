import os
import sys
import django
from django.test import TestCase
from banking_api import models
import uuid
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

def test_user_model():
    user = models.User.objects.create(
        username='testuser',
        email='test@example.com',
        balance=1000,
        daily_transaction_limit=5000
    )
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.balance == 1000
    assert user.daily_transaction_limit == 5000

def test_api_key_model():
    api_key = models.ApiKey.objects.create(
        key='test-key-123',
        name='Test API Key',
        rate_limit=100,
        ip_whitelist=['192.168.1.1'],
        allowed_methods=['GET', 'POST']
    )
    
    assert api_key.name == 'Test API Key'
    assert api_key.rate_limit == 100
    assert api_key.ip_whitelist == ['192.168.1.1']

def test_transaction_model():
    user = models.User.objects.create(
        username='testuser',
        email='test@example.com',
        balance=1000
    )
    
    transaction = models.Transaction.objects.create(
        transaction_id=str(uuid.uuid4()),
        source_system='test-system',
        target_system='bank-system',
        transaction_type='deposit',
        status='pending',
        amount=500,
        currency='USD',
        user=user,
        request_data={'amount': 500}
    )
    
    assert transaction.status == 'pending'
    assert transaction.amount == 500
    assert transaction.currency == 'USD'

if __name__ == '__main__':
    print("Running tests...")
    test_user_model()
    test_api_key_model()
    test_transaction_model()
    print("All tests passed!")
