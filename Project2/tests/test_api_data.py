import uuid
import pytest
import json
import io
from test_helpers import setup_admin_session, setup_user_session


def test_data_export(client):
    """Test GET /api/export/"""
    # Set up admin session
    setup_admin_session(client)
    
    # Create some data to export
    # Create problem
    problem_id = "export_test_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "导出测试题目",
        "description": "计算a+b",
        "input_description": "两个整数",
        "output_description": "它们的和",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2", "output": "3"}],
        "time_limit": "1s",
        "memory_limit": "128MB"
    }
    client.post("/api/problems/", json=problem_data)
    
    # Create user
    username = "export_user_" + uuid.uuid4().hex[:8]
    password = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": username, "password": password}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, username, password)
    
    # Submit solution
    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }
    client.post("/api/submissions/", json=submission_data)
    
    # Switch to admin session and export data
    setup_admin_session(client)
    
    # Export data (default format)
    response = client.get("/api/export/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert "users" in data["data"]
    assert "problems" in data["data"]
    assert "submissions" in data["data"]
    assert isinstance(data["data"]["users"], list)
    assert isinstance(data["data"]["problems"], list)
    assert isinstance(data["data"]["submissions"], list)
    
    # Test with specific format
    response = client.get("/api/export/?format=json")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    
    # Test non-admin access
    setup_user_session(client, username, password)
    response = client.get("/api/export/")
    assert response.status_code == 403


def test_data_import(client):
    """Test POST /api/import/"""
    # Set up admin session
    setup_admin_session(client)
    
    # Prepare test data for import
    import_data = {
        "users": [
            {"username": "imported_user_" + uuid.uuid4().hex[:4], "password": "pw123", "role": "user"}
        ],
        "problems": [
            {
                "id": "imported_problem_" + uuid.uuid4().hex[:4],
                "title": "导入测试题目",
                "description": "计算a+b",
                "input_description": "两个整数",
                "output_description": "它们的和",
                "samples": [{"input": "1 2", "output": "3"}],
                "constraints": "|a|,|b| <= 10^9",
                "testcases": [{"input": "1 2", "output": "3"}],
                "time_limit": "1s",
                "memory_limit": "128MB"
            }
        ],
        "submissions": []
    }
    
    # Convert to JSON bytes for file upload
    json_data = json.dumps(import_data).encode('utf-8')
    
    # Create a file-like object
    file_obj = io.BytesIO(json_data)
    
    # Test import (Note: This test assumes the API accepts JSON data)
    # In a real implementation, this might need to be adjusted based on 
    # how the file upload is handled
    files = {"file": ("import.json", file_obj, "application/json")}
    
    response = client.post("/api/import/", files=files)
    assert response.status_code == 200
    
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "import success"
    assert "data" in data
    assert "imported_counts" in data["data"]
    
    # Verify import worked
    counts = data["data"]["imported_counts"]
    assert counts["users"] == 1
    assert counts["problems"] == 1
    assert counts["submissions"] == 0
    
    # Test with invalid data
    invalid_data = b"invalid json data"
    invalid_file = io.BytesIO(invalid_data)
    files = {"file": ("invalid.json", invalid_file, "application/json")}
    
    response = client.post("/api/import/", files=files)
    assert response.status_code == 400
    
    # Test non-admin access
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": user, "password": upw}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, user, upw)
    
    valid_file = io.BytesIO(json.dumps(import_data).encode('utf-8'))
    files = {"file": ("test.json", valid_file, "application/json")}
    
    response = client.post("/api/import/", files=files)
    assert response.status_code == 403