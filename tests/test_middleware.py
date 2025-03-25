import json
import pytest
from app import create_app, db
from models import User, SystemConfig, ApiKey, Transaction


@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app("testing")

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create a test user
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)

            # Create test system configs
            fsp_api_key = ApiKey(
                name="test_fsp_key",
                key_value="test_fsp_key_value",
                secret_value="test_fsp_secret",
                provider_type="financial_provider",
                is_active=True,
            )
            db.session.add(fsp_api_key)
            db.session.flush()

            banking_api_key = ApiKey(
                name="test_banking_key",
                key_value="test_banking_key_value",
                secret_value="test_banking_secret",
                provider_type="banking_system",
                is_active=True,
            )
            db.session.add(banking_api_key)
            db.session.flush()

            # FSP config
            fsp_config = SystemConfig(
                system_name="test_fsp",
                system_type="financial_provider",
                base_url="http://localhost:8002/api",
                auth_type="api_key",
                api_key_id=fsp_api_key.id,
                is_active=True,
            )
            db.session.add(fsp_config)

            # Banking system config
            banking_config = SystemConfig(
                system_name="test_banking",
                system_type="banking_system",
                base_url="http://localhost:8001/api",
                auth_type="api_key",
                api_key_id=banking_api_key.id,
                is_active=True,
            )
            db.session.add(banking_config)

            db.session.commit()

            yield client

            # Clean up
            db.session.remove()
            db.drop_all()


def get_auth_token(client):
    """Helper function to get auth token for tests."""
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password"}
    )
    data = json.loads(response.data)
    return data["access_token"]


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/middleware/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert data["service"] == "banking_middleware"


def test_process_transaction_validation(client):
    """Test validation of transaction processing."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Missing required fields
    response = client.post("/api/v1/middleware/transaction", json={}, headers=headers)
    assert response.status_code == 400

    # Invalid transaction type
    response = client.post(
        "/api/v1/middleware/transaction",
        json={
            "source_system": "test_banking",
            "target_system": "test_fsp",
            "transaction_type": "invalid_type",
        },
        headers=headers,
    )
    assert response.status_code == 400


def test_get_transaction_status_not_found(client):
    """Test getting status of non-existent transaction."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/middleware/status/nonexistent", headers=headers)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Transaction not found"


def test_get_transactions_list(client):
    """Test getting list of transactions."""
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/middleware/transactions", headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "transactions" in data
    assert "meta" in data
