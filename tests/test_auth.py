import json
import pytest
from app import create_app, db
from models import User


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
            db.session.commit()

            yield client

            # Clean up
            db.session.remove()
            db.drop_all()


def test_login_success(client):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Invalid username or password"


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword",
        },
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert "message" in data
    assert "user" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "new@example.com"


def test_register_existing_username(client):
    """Test registration with existing username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "newpassword",
        },
    )

    assert response.status_code == 409
    data = json.loads(response.data)
    assert "error" in data
    assert data["error"] == "Username already exists"


def test_refresh_token(client):
    """Test refreshing access token."""
    # First login to get refresh token
    login_response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password"}
    )
    login_data = json.loads(login_response.data)
    refresh_token = login_data["refresh_token"]

    # Use refresh token to get new access token
    response = client.post(
        "/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data


def test_verify_token(client):
    """Test verifying a valid token."""
    # First login to get access token
    login_response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "password"}
    )
    login_data = json.loads(login_response.data)
    access_token = login_data["access_token"]

    # Verify the token
    response = client.post(
        "/api/v1/auth/verify", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "valid" in data
    assert data["valid"] is True
    assert "user" in data
    assert data["user"]["username"] == "testuser"
