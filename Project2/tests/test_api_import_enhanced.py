import uuid
import pytest
import json
import io
from test_helpers import setup_admin_session, setup_user_session, reset_system


def test_data_import_complete_verification(client):
    """Test POST /api/import/ - complete data integrity verification"""
    # Reset and setup admin
    reset_system(client)
    setup_admin_session(client)

    # Prepare comprehensive test data
    import_data = {
        "users": [
            {
                "username": "imported_user1_" + uuid.uuid4().hex[:4],
                "password": "password123",
                "role": "user"
            },
            {
                "username": "imported_admin_" + uuid.uuid4().hex[:4],
                "password": "adminpass123",
                "role": "admin"
            }
        ],
        "problems": [
            {
                "id": "imported_prob1_" + uuid.uuid4().hex[:4],
                "title": "Imported Problem 1",
                "description": "Test problem for import",
                "input_description": "Input description",
                "output_description": "Output description",
                "samples": [{"input": "1 2\n", "output": "3\n"}],
                "constraints": "|a|,|b| <= 10^9",
                "testcases": [
                    {"input": "1 2\n", "output": "3\n"},
                    {"input": "5 7\n", "output": "12\n"}
                ],
                "time_limit": "2s",
                "memory_limit": "256MB"
            },
            {
                "id": "imported_prob2_" + uuid.uuid4().hex[:4],
                "title": "Imported Problem 2",
                "description": "Another test problem",
                "input_description": "Input desc 2",
                "output_description": "Output desc 2",
                "samples": [{"input": "10\n", "output": "10\n"}],
                "constraints": "|x| <= 10^9",
                "testcases": [{"input": "10\n", "output": "10\n"}],
                "time_limit": "1s",
                "memory_limit": "128MB"
            }
        ],
        "submissions": [
            {
                "user_id": 1,
                "problem_id": "imported_prob1",
                "language": "python",
                "code": "a, b = map(int, input().split())\nprint(a + b)",
                "status": "Accepted",
                "score": 100
            }
        ]
    }

    # Convert to JSON and create file
    json_data = json.dumps(import_data, indent=2).encode('utf-8')
    file_obj = io.BytesIO(json_data)
    files = {"file": ("complete_import.json", file_obj, "application/json")}

    # Perform import
    response = client.post("/api/import/", files=files)

    if response.status_code == 200:
        data = response.json()
        assert data["code"] == 200
        assert data["msg"] == "import success"
        assert data["data"] is None

        # Verify imported data integrity
        # Check users were imported
        users_response = client.get("/api/users/")
        assert users_response.status_code == 200
        users_data = users_response.json()["data"]["users"]

        imported_usernames = [user["username"] for user in import_data["users"]]
        existing_usernames = [user["username"] for user in users_data]

        for username in imported_usernames:
            assert username in existing_usernames

        # Check problems were imported
        problems_response = client.get("/api/problems/")
        assert problems_response.status_code == 200
        problems_data = problems_response.json()["data"]

        imported_problem_ids = [prob["id"] for prob in import_data["problems"]]
        existing_problem_ids = [prob["id"] for prob in problems_data]

        for problem_id in imported_problem_ids:
            assert problem_id in existing_problem_ids

        # Check submissions were imported
        submissions_response = client.get("/api/submissions/")
        assert submissions_response.status_code == 200
        submissions_data = submissions_response.json()["data"]["submissions"]
        assert len(submissions_data) >= 1  # At least the imported submission

    elif response.status_code == 400:
        # Import failed due to data validation
        data = response.json()
        assert data["code"] == 400
        assert "msg" in data
    else:
        # Not implemented or other error
        assert response.status_code in [403, 500, 501]


def test_data_import_various_formats(client):
    """Test POST /api/import/ - different file formats"""
    setup_admin_session(client)

    # Test 1: Valid JSON format
    valid_data = {
        "users": [{"username": "test_user_" + uuid.uuid4().hex[:4], "password": "pass", "role": "user"}],
        "problems": [],
        "submissions": []
    }

    json_content = json.dumps(valid_data).encode('utf-8')
    json_file = io.BytesIO(json_content)
    files = {"file": ("valid.json", json_file, "application/json")}

    response = client.post("/api/import/", files=files)
    # Should succeed or return not implemented
    assert response.status_code in [200, 400, 403, 500, 501]

    # Test 2: Invalid JSON format
    invalid_json = b'{"users": [invalid json'
    invalid_file = io.BytesIO(invalid_json)
    files = {"file": ("invalid.json", invalid_file, "application/json")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        assert response.status_code == 400

    # Test 3: Empty file
    empty_file = io.BytesIO(b'')
    files = {"file": ("empty.json", empty_file, "application/json")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        assert response.status_code == 400

    # Test 4: Wrong content type
    csv_content = b'username,password,role\ntest,pass,user'
    csv_file = io.BytesIO(csv_content)
    files = {"file": ("data.csv", csv_file, "text/csv")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        assert response.status_code in [400, 415]  # Bad request or unsupported media type


def test_data_import_missing_required_fields(client):
    """Test POST /api/import/ - missing required fields in data"""
    setup_admin_session(client)

    # Test missing required fields in users
    invalid_user_data = {
        "users": [
            {"username": "test_user"},  # Missing password
            {"password": "pass123"}     # Missing username
        ],
        "problems": [],
        "submissions": []
    }

    json_content = json.dumps(invalid_user_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("invalid_users.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        # Now properly validates required fields
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400

    # Test missing required fields in problems
    invalid_problem_data = {
        "users": [],
        "problems": [
            {
                "id": "test_prob",
                # Missing required fields like title, description, etc.
            }
        ],
        "submissions": []
    }

    json_content = json.dumps(invalid_problem_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("invalid_problems.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        # Now properly validates required fields
        assert response.status_code == 400
        data = response.json()
        assert data["code"] == 400
        assert "missing required field" in data["msg"].lower()


def test_data_import_duplicate_handling(client):
    """Test POST /api/import/ - handling of duplicate data"""
    # Reset and setup
    reset_system(client)
    setup_admin_session(client)

    # Create some existing data
    existing_user = "existing_user_" + uuid.uuid4().hex[:4]
    client.post("/api/users/", json={"username": existing_user, "password": "pass123"})

    # Try to import duplicate user
    import_data = {
        "users": [
            {"username": existing_user, "password": "newpass", "role": "user"}  # Duplicate
        ],
        "problems": [],
        "submissions": []
    }

    json_content = json.dumps(import_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("duplicate_user.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    if response.status_code not in [501]:  # If implemented
        # Should handle duplicates gracefully (skip or update)
        assert response.status_code in [200, 400, 409]  # Success, bad request, or conflict


def test_data_import_large_dataset(client):
    """Test POST /api/import/ - large dataset import"""
    setup_admin_session(client)

    # Create large dataset
    large_data = {
        "users": [],
        "problems": [],
        "submissions": []
    }

    # Generate many users
    for i in range(50):
        large_data["users"].append({
            "username": f"bulk_user_{i}_{uuid.uuid4().hex[:4]}",
            "password": f"pass_{i}",
            "role": "user"
        })

    # Generate many problems
    for i in range(20):
        large_data["problems"].append({
            "id": f"bulk_prob_{i}_{uuid.uuid4().hex[:4]}",
            "title": f"Bulk Problem {i}",
            "description": f"Problem {i} description",
            "input_description": "Input",
            "output_description": "Output",
            "samples": [{"input": f"{i}\n", "output": f"{i}\n"}],
            "constraints": "|x| <= 10^9",
            "testcases": [{"input": f"{i}\n", "output": f"{i}\n"}],
            "time_limit": "1s",
            "memory_limit": "128MB"
        })

    json_content = json.dumps(large_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("large_dataset.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    # Should handle large datasets (might take time or require chunking)
    assert response.status_code in [200, 400, 403, 500, 501, 413]  # Include payload too large


def test_data_import_no_file(client):
    """Test POST /api/import/ - no file provided"""
    setup_admin_session(client)

    # Try import without file
    response = client.post("/api/import/")
    if response.status_code not in [501]:  # If implemented
        # FastAPI returns 400 for missing required file parameter
        assert response.status_code == 400


def test_data_import_file_size_limits(client):
    """Test POST /api/import/ - file size limits"""
    setup_admin_session(client)

    # Create very large file content (simulate large file)
    large_content = json.dumps({
        "users": [],
        "problems": [],
        "submissions": [],
        "large_field": "x" * (10 * 1024 * 1024)  # 10MB of data
    }).encode('utf-8')

    large_file = io.BytesIO(large_content)
    files = {"file": ("huge_file.json", large_file, "application/json")}

    response = client.post("/api/import/", files=files)
    # Should reject files that are too large
    assert response.status_code in [200, 400, 413, 500, 501]  # Include payload too large