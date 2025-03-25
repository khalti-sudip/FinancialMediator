import pytest
from flask import json
from models import KYC, db


@pytest.fixture
def client():
    """Create test client"""
    from yourapplication import app

    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_headers():
    """Create authentication headers"""
    # Replace with your actual authentication logic
    return {"Authorization": "Bearer your_token"}


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    # Replace with your actual user creation logic
    return User(id=1, username="testuser", email="test@example.com")


def test_kyc_creation_flow(client, auth_headers, sample_user):
    """Test complete KYC flow"""
    kyc_data = {
        "full_name": "Test User",
        "phone_number": "9876543210",
        "address": "Test Address",
        "document_type": "citizenship",
        "document_number": "123456789",
    }

    response = client.post("/api/kyc", headers=auth_headers, json=kyc_data)

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["full_name"] == "Test User"
    assert data["status"] == "pending"

    # Verify database state
    kyc = KYC.query.filter_by(user_id=sample_user.id).first()
    assert kyc is not None
    assert kyc.full_name == "Test User"
    assert kyc.document_type == "citizenship"


def test_get_kyc(client, auth_headers, sample_user):
    """Test retrieving KYC information"""
    # Create a KYC record
    kyc = KYC(
        user_id=sample_user.id,
        full_name="Test User",
        phone_number="1234567890",
        address="Test Address",
        status="pending",
    )
    db.session.add(kyc)
    db.session.commit()

    response = client.get(f"/api/kyc/{kyc.id}", headers=auth_headers)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["full_name"] == "Test User"
    assert data["status"] == "pending"


def test_update_kyc_status(client, auth_headers, sample_user):
    """Test updating KYC status"""
    # Create a KYC record
    kyc = KYC(
        user_id=sample_user.id,
        full_name="Test User",
        phone_number="1234567890",
        address="Test Address",
        status="pending",
    )
    db.session.add(kyc)
    db.session.commit()

    update_data = {"status": "approved"}

    response = client.put(f"/api/kyc/{kyc.id}", headers=auth_headers, json=update_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "approved"

    # Verify database state
    kyc = KYC.query.get(kyc.id)
    assert kyc.status == "approved"
    assert kyc.verified_at is not None
