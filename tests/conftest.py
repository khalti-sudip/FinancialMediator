import pytest
import os
import django
from django.test import Client
from django.contrib.auth.models import User
from banking_api.models import User as BankingUser, ApiKey, Transaction
from django.conf import settings
import uuid

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def client():
    """Create Django test client."""
    return Client()

@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    # Create test user and get token
    user = BankingUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    
    # In a real application, you would use your authentication system
    # For now, we'll just return a mock header
    return {"Authorization": "Bearer test-token"}

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return BankingUser.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        balance=1000,
        daily_transaction_limit=5000
    )

@pytest.fixture
def sample_api_key():
    """Create a sample API key for testing."""
    return ApiKey.objects.create(
        key="test-key-123",
        name="Test API Key",
        rate_limit=100,
        ip_whitelist=["192.168.1.1"],
        allowed_methods=["GET", "POST"]
    )

@pytest.fixture
def sample_transaction(sample_user):
    """Create a sample transaction for testing."""
    return Transaction.objects.create(
        transaction_id=str(uuid.uuid4()),
        source_system="test-system",
        target_system="bank-system",
        transaction_type="deposit",
        status="pending",
        amount=500,
        currency="USD",
        user=sample_user,
        request_data={"amount": 500}
    )
