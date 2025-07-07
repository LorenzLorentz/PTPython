import uuid
import pytest
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user


def test_user_register(client):
    """Test POST /api/users/"""
    username = "test_user_" + uuid.uuid4().hex[:8]
    password = "test_pw_" + uuid.uuid4().hex[:8]
    
    user_data = {
        "username": username,
        "password": password
    }
    
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "register success"
    assert "data" in data
    assert "user_id" in data["data"]
    
    # Test duplicate username
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 400
    
    # Test missing parameters
    response = client.post("/api/users/", json={"username": "test"})
    assert response.status_code == 400


def test_get_user_info(client):
    """Test GET /api/users/{user_id}"""
    # Reset system and create admin
    reset_system(client)
    
    # Create user via API
    username, password, user_id = create_test_user(client)
    
    # Get user info (as admin)
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert data["data"]["user_id"] == user_id
    assert data["data"]["username"] == username
    assert data["data"]["role"] == "user"
    
    # Test non-existent user
    response = client.get("/api/users/999999")
    assert response.status_code == 404


def test_update_user_role(client):
    """Test PUT /api/users/{user_id}/role"""
    # Reset system
    reset_system(client)
    
    # Create user via API
    username, password, user_id = create_test_user(client)
    
    # Update user role
    role_data = {"role": "admin"}
    response = client.put(f"/api/users/{user_id}/role", json=role_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "role updated"
    assert data["data"]["user_id"] == user_id
    assert data["data"]["role"] == "admin"
    
    # Test non-existent user
    response = client.put("/api/users/999999/role", json=role_data)
    assert response.status_code == 404


def test_get_users_list(client):
    """Test GET /api/users/"""
    # Reset system
    reset_system(client)
    
    # Create some users via API
    for i in range(3):
        create_test_user(client)
    
    # Get users list
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert "total" in data["data"]
    assert "users" in data["data"]
    assert isinstance(data["data"]["users"], list)
    assert data["data"]["total"] >= 3