import uuid
import pytest
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user


def test_system_reset_success(client):
    """Test POST /api/reset/ - successful reset"""
    # Set up admin session
    setup_admin_session(client)

    # Create some data first
    problem_data = {
        "id": "reset_test_" + uuid.uuid4().hex[:4],
        "title": "Reset Test Problem",
        "description": "Test problem for reset",
        "input_description": "Input",
        "output_description": "Output",
        "samples": [{"input": "1\n", "output": "1\n"}],
        "testcases": [{"input": "1\n", "output": "1\n"}],
        "constraints": "|x| <= 10^9",
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)

    # Verify problem exists
    response = client.get("/api/problems/")
    problems_before = response.json()["data"]
    assert len(problems_before) > 0

    # Reset system
    response = client.post("/api/reset/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "system reset successfully"
    assert data["data"] is None

    # Verify data is cleared
    setup_admin_session(client)  # Re-authenticate after reset
    response = client.get("/api/problems/")
    problems_after = response.json()["data"]
    assert len(problems_after) == 0


def test_system_reset_admin_only(client):
    """Test POST /api/reset/ - requires admin privileges"""
    # Create regular user
    username, password, user_id = create_test_user(client)

    # Try reset as regular user
    setup_user_session(client, username, password)
    response = client.post("/api/reset/")
    assert response.status_code in [401, 403]


def test_system_reset_no_auth(client):
    """Test POST /api/reset/ - requires authentication"""
    # Try reset without authentication
    response = client.post("/api/reset/")
    assert response.status_code in [401, 403]


def test_system_reset_recreates_admin(client):
    """Test POST /api/reset/ - recreates initial admin"""
    setup_admin_session(client)

    # Reset system
    response = client.post("/api/reset/")
    assert response.status_code == 200

    # Verify admin still exists and works
    setup_admin_session(client, "admin")
    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200

    # Find admin user in the list
    admin_found = False
    for user in data["data"]["users"]:
        if user["username"] == "admin":
            admin_found = True
            break
    assert admin_found, "Admin user should exist after reset"