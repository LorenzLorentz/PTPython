"""Common test helpers that only use documented APIs"""
import uuid


def setup_admin_session(client, admin_username="admin", admin_password="admintestpassword"):
    """Helper to set up admin session for testing using proper login"""
    response = client.post("/api/auth/login", json={
        "username": admin_username,
        "password": admin_password
    })
    if response.status_code != 200:
        raise Exception(f"Failed to login admin: {response.json()}")
    return response.json()["data"]


def setup_user_session(client, username, password="testpass"):
    """Helper to set up user session for testing using proper login"""
    response = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code != 200:
        raise Exception(f"Failed to login user: {response.json()}")
    return response.json()["data"]


def reset_system(client):
    """Helper to reset system using documented API"""
    # Login as default admin and reset
    setup_admin_session(client, "admin")
    client.post("/api/reset/")


def create_test_admin(client, username=None, password=None):
    """Helper to create a test admin using documented API"""
    # Login as default admin
    setup_admin_session(client, "admin")
    
    if username is None:
        username = "test_admin_" + uuid.uuid4().hex[:8]
    if password is None:
        password = "admin_pw_" + uuid.uuid4().hex[:8]
    
    admin_data = {
        "username": username,
        "password": password
    }
    
    response = client.post("/api/users/admin", json=admin_data)
    if response.status_code == 200:
        return username, password, response.json()["data"]["user_id"]
    else:
        raise Exception(f"Failed to create admin: {response.json()}")


def create_test_user(client, username=None, password=None):
    """Helper to create a test user using documented API"""
    if username is None:
        username = "test_user_" + uuid.uuid4().hex[:8]
    if password is None:
        password = "user_pw_" + uuid.uuid4().hex[:8]
    
    user_data = {
        "username": username,
        "password": password
    }
    
    response = client.post("/api/users/", json=user_data)
    if response.status_code == 200:
        return username, password, response.json()["data"]["user_id"]
    else:
        raise Exception(f"Failed to create user: {response.json()}")


def create_test_problem(client, problem_id=None):
    """Helper to create a test problem using documented API"""
    if problem_id is None:
        problem_id = "test_problem_" + uuid.uuid4().hex[:4]
    
    problem_data = {
        "id": problem_id,
        "title": "测试题目",
        "description": "计算a+b",
        "input_description": "两个整数",
        "output_description": "它们的和",
        "samples": [{"input": "1 2\n", "output": "3\n"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2\n", "output": "3\n"}],
        "time_limit": 1.0,
        "memory_limit": 128
    }
    
    response = client.post("/api/problems/", json=problem_data)
    if response.status_code == 200:
        return problem_id, problem_data
    else:
        raise Exception(f"Failed to create problem: {response.json()}")