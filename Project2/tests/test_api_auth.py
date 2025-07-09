"""Tests for authentication endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuth:
    """Test authentication endpoints"""

    def test_login_success_admin(self):
        """Test successful admin login"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "login success"
        assert data["data"]["username"] == "admin"
        assert data["data"]["role"] == "admin"

    def test_login_success_user(self):
        """Test successful user login"""
        # First create a user
        client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
        client.post("/api/users/", json={
            "username": "testuser",
            "password": "testpass"
        })
        client.post("/api/auth/logout")

        # Now test user login
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "login success"
        assert data["data"]["username"] == "testuser"
        assert data["data"]["role"] == "user"

    def test_login_invalid_username(self):
        """Test login with invalid username"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401

    def test_login_invalid_password(self):
        """Test login with invalid password"""
        response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrongpass"
        })
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = client.post("/api/auth/login", json={
            "username": "admin"
        })
        assert response.status_code == 400  # Parameter error

    def test_logout_success(self):
        """Test successful logout"""
        # First login
        client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin"
        })

        # Then logout
        response = client.post("/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "logout success"
        assert data["data"] is None

    def test_logout_not_logged_in(self):
        """Test logout when not logged in"""
        # Make sure we're not logged in
        client.post("/api/auth/logout")  # Clear any existing session

        response = client.post("/api/auth/logout")
        assert response.status_code == 401
        data = response.json()
        assert data["code"] == 401

    def test_session_persistence(self):
        """Test that session persists across requests"""
        # Login
        login_response = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin"
        })
        assert login_response.status_code == 200

        # Make an authenticated request (get user info)
        user_response = client.get("/api/users/1")
        assert user_response.status_code == 200

        # Logout
        logout_response = client.post("/api/auth/logout")
        assert logout_response.status_code == 200

        # Try authenticated request after logout (should fail)
        user_response_after_logout = client.get("/api/users/1")
        assert user_response_after_logout.status_code == 401