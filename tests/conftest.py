import pytest
from flask import json
from app import create_app, db
from models import User, Provider


@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers."""
    # Create test user and get JWT token
    user = User(username="testuser", email="test@example.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()

    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    token = json.loads(response.data)["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def sample_provider():
    """Create a sample provider for testing."""
    provider = Provider(
        name="Test Provider",
        api_key="test-key",
        api_secret="test-secret",
        status="active",
        provider_type="payment",
        base_url="https://api.testprovider.com",
    )
    db.session.add(provider)
    db.session.commit()
    return provider
