import uuid
import time
import pytest
from test_helpers import setup_admin_session, setup_user_session


def test_get_submission_log(client):
    """Test GET /api/submissions/{submission_id}/log"""
    # Set up admin session
    setup_admin_session(client)
    
    problem_id = "test_log_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "日志测试",
        "description": "计算a+b",
        "input_description": "两个整数",
        "output_description": "它们的和",
        "samples": [{"input": "1 2\n", "output": "3\n"}],
        "testcases": [
            {"input": "1 2\n", "output": "3\n"},
            {"input": "10 20\n", "output": "30\n"}
        ],
        "constraints": "|a|,|b| <= 10^9",
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)
    
    # Create user and submit
    username = "log_user_" + uuid.uuid4().hex[:8]
    password = "pw_" + uuid.uuid4().hex[:8]
    client.post("/api/users/", json={"username": username, "password": password})
    setup_user_session(client, username, password)
    
    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }
    
    submit_response = client.post("/api/submissions/", json=submission_data)
    submission_id = submit_response.json()["data"]["submission_id"]
    
    # Wait for judging
    time.sleep(2)
    
    # Get submission log (as user)
    response = client.get(f"/api/submissions/{submission_id}/log")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert isinstance(data["data"], dict)
    
    # Check the new API spec structure
    assert "status" in data["data"]
    assert "score" in data["data"]
    assert "counts" in data["data"]
    
    # Assert specific expected values based on test case
    # Problem has 2 test cases, each worth 10 points, correct solution should get full score
    assert data["data"]["score"] == 20  # 2 test cases × 10 points each
    assert data["data"]["counts"] == 20  # Total possible points
    
    # Check status array has exactly 2 test cases with specific expected results
    assert len(data["data"]["status"]) == 2  # Should have exactly 2 test cases
    
    # Sort by id to ensure consistent ordering
    status_items = sorted(data["data"]["status"], key=lambda x: x["id"])
    
    # Test case 1: input "1 2" -> output "3" (should be AC)
    assert status_items[0]["id"] == 1
    assert status_items[0]["result"] == "AC"
    
    # Test case 2: input "10 20" -> output "30" (should be AC)
    assert status_items[1]["id"] == 2
    assert status_items[1]["result"] == "AC"
    
    # Test as admin
    setup_admin_session(client)
    response = client.get(f"/api/submissions/{submission_id}/log")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Test non-existent submission
    response = client.get("/api/submissions/999999/log")
    assert response.status_code == 404
    
    # Test unauthorized access
    other_user = "other_user_" + uuid.uuid4().hex[:8]
    other_pw = "pw_" + uuid.uuid4().hex[:8]
    client.post("/api/users/", json={"username": other_user, "password": other_pw})
    setup_user_session(client, other_user, other_pw)
    
    response = client.get(f"/api/submissions/{submission_id}/log")
    assert response.status_code == 403


def test_configure_log_visibility(client):
    """Test PUT /api/problems/{problem_id}/log_visibility"""
    # Set up admin session
    setup_admin_session(client)
    
    problem_id = "test_visibility_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "可见性测试",
        "description": "计算a+b",
        "input_description": "两个整数",
        "output_description": "它们的和",
        "samples": [{"input": "1 2\n", "output": "3\n"}],
        "testcases": [{"input": "1 2\n", "output": "3\n"}],
        "constraints": "|a|,|b| <= 10^9",
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)
    
    # Configure log visibility
    visibility_data = {"public_cases": True}
    response = client.put(f"/api/problems/{problem_id}/log_visibility", json=visibility_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "log visibility updated"
    assert data["data"]["problem_id"] == problem_id
    assert data["data"]["public_cases"] == True
    
    # Test disable visibility
    visibility_data = {"public_cases": False}
    response = client.put(f"/api/problems/{problem_id}/log_visibility", json=visibility_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["public_cases"] == False
    
    # Test non-existent problem
    response = client.put("/api/problems/nonexistent/log_visibility", json=visibility_data)
    assert response.status_code == 404
    
    # Test non-admin access
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    client.post("/api/users/", json={"username": user, "password": upw})
    setup_user_session(client, user, upw)
    
    response = client.put(f"/api/problems/{problem_id}/log_visibility", json=visibility_data)
    assert response.status_code == 403


def test_access_audit_logs(client):
    """Test GET /api/logs/access/"""
    # Set up admin session
    setup_admin_session(client)
    
    # Create problem and user
    problem_id = "test_audit_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "审计测试",
        "description": "计算a+b",
        "input_description": "两个整数",
        "output_description": "它们的和",
        "samples": [{"input": "1 2\n", "output": "3\n"}],
        "testcases": [{"input": "1 2\n", "output": "3\n"}],
        "constraints": "|a|,|b| <= 10^9",
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)
    
    username = "audit_user_" + uuid.uuid4().hex[:8]
    password = "pw_" + uuid.uuid4().hex[:8]
    client.post("/api/users/", json={"username": username, "password": password})
    setup_user_session(client, username, password)
    
    # Create some activity (submission and log access)
    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }
    
    submit_response = client.post("/api/submissions/", json=submission_data)
    submission_id = submit_response.json()["data"]["submission_id"]
    time.sleep(1)
    
    # Access submission log to generate audit trail
    client.get(f"/api/submissions/{submission_id}/log")
    
    # Login as admin and get audit logs
    setup_admin_session(client)
    
    # Get all access logs
    response = client.get("/api/logs/access/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)
    
    # Test with user_id filter
    user_id = "1"  # API uses string IDs
    response = client.get(f"/api/logs/access/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Test with problem_id filter
    response = client.get(f"/api/logs/access/?problem_id={problem_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Test with pagination
    response = client.get("/api/logs/access/?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Test non-admin access
    setup_user_session(client, username, password)
    response = client.get("/api/logs/access/")
    assert response.status_code == 403