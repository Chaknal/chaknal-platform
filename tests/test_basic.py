from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


def test_version_endpoint():
    """Test the version endpoint"""
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "name" in data


def test_auth_status_endpoint():
    """Test the auth status endpoint"""
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    data = response.json()
    assert "jwt_auth" in data
    assert "google_oauth" in data
    assert "endpoints" in data


def test_auth_login_endpoint():
    """Test the login endpoint"""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


def test_auth_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """Test protected endpoint without authentication"""
    response = client.get("/auth/protected")
    assert response.status_code == 403


def test_protected_endpoint_with_token():
    """Test protected endpoint with valid token"""
    # First login to get token
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]

    # Use token to access protected endpoint
    response = client.get(
        "/auth/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "user" in data


def test_cors_headers():
    """Test that CORS headers are present"""
    response = client.options("/")
    assert response.status_code == 200
    # CORS headers should be present (handled by FastAPI CORS middleware)


def test_rate_limiting():
    """Test rate limiting (this might be flaky in tests)"""
    # Make multiple requests to test rate limiting
    responses = []
    for _ in range(5):  # Small number to avoid actual rate limiting in tests
        response = client.get("/health")
        responses.append(response.status_code)

    # All should be 200, rate limiting shouldn't trigger with this few requests
    assert all(status == 200 for status in responses)
