import uuid
import pytest
from test_helpers import setup_admin_session, setup_user_session, create_test_user


def test_create_admin_account(client):
    """Test POST /api/users/admin"""
    # Log in as default admin
    setup_admin_session(client)
    
    # Create new admin
    new_admin_username = "new_admin_" + uuid.uuid4().hex[:8]
    new_admin_password = "admin_pw_" + uuid.uuid4().hex[:8]
    
    admin_data = {
        "username": new_admin_username,
        "password": new_admin_password
    }
    
    response = client.post("/api/users/admin", json=admin_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "admin created successfully"
    assert "data" in data
    assert "user_id" in data["data"]
    assert data["data"]["username"] == new_admin_username
    
    # Verify the new admin can perform admin operations
    setup_admin_session(client, new_admin_username, new_admin_password)
    
    # Test that new admin can create another admin
    another_admin = "another_admin_" + uuid.uuid4().hex[:8]
    another_password = "pw_" + uuid.uuid4().hex[:8]
    
    response = client.post("/api/users/admin", json={
        "username": another_admin,
        "password": another_password
    })
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200


def test_create_admin_duplicate_username(client):
    """Test creating admin with duplicate username"""
    # Log in as default admin
    setup_admin_session(client)
    
    # Try to create admin with existing username "admin"
    admin_data = {
        "username": "admin",
        "password": "newpassword"
    }
    
    response = client.post("/api/users/admin", json=admin_data)
    assert response.status_code == 400
    data = response.json()
    assert "already exists" in data["detail"].lower()


def test_create_admin_missing_fields(client):
    """Test creating admin with missing required fields"""
    # Log in as default admin
    setup_admin_session(client)
    
    # Test missing username
    response = client.post("/api/users/admin", json={"password": "test123"})
    assert response.status_code == 400
    
    # Test missing password
    response = client.post("/api/users/admin", json={"username": "testadmin"})
    assert response.status_code == 400
    
    # Test missing both
    response = client.post("/api/users/admin", json={})
    assert response.status_code == 400


def test_create_admin_non_admin_access(client):
    """Test that non-admin users cannot create admin accounts"""
    # Create regular user
    username, password, user_id = create_test_user(client)
    
    # Log in as regular user
    setup_user_session(client, username, password)
    
    # Try to create admin
    admin_data = {
        "username": "unauthorized_admin_" + uuid.uuid4().hex[:8],
        "password": "admin_pw"
    }
    
    response = client.post("/api/users/admin", json=admin_data)
    assert response.status_code == 403


def test_create_admin_no_auth(client):
    """Test creating admin without authentication"""
    admin_data = {
        "username": "no_auth_admin_" + uuid.uuid4().hex[:8],
        "password": "admin_pw"
    }
    
    response = client.post("/api/users/admin", json=admin_data)
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden


def test_initial_admin_exists(client):
    """Test that initial admin account exists and works"""
    # Test login as default admin
    setup_admin_session(client, "admin")
    
    # Test that default admin can perform admin operations
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Verify admin user exists in the user list
    users = data["data"]["users"]
    admin_found = any(user["username"] == "admin" and user["role"] == "admin" for user in users)
    assert admin_found, "Initial admin user not found in user list"