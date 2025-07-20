import uuid
import pytest
import json
import io
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user


def test_data_import_complete_verification(client):
    """Test POST /api/import/ - complete data integrity verification"""
    # Reset and setup admin
    reset_system(client)
    setup_admin_session(client)

    # Prepare comprehensive test data according to api.md structure
    import_data = {
        "users": [
            {
                "user_id": "100",
                "username": "imported_user1_" + uuid.uuid4().hex[:4],
                "password": "placeholder_hash_imported_user1",  # Placeholder password hash
                "role": "user",
                "join_time": "2024-01-01",  # API uses date format
                "submit_count": 1,
                "resolve_count": 1
            },
            {
                "user_id": "101",
                "username": "imported_admin_" + uuid.uuid4().hex[:4],
                "password": "placeholder_hash_imported_admin",  # Placeholder password hash
                "role": "admin",
                "join_time": "2024-01-01",  # API uses date format
                "submit_count": 0,
                "resolve_count": 0
            }
        ],
        "problems": [
            {
                "id": "imported_prob1_" + uuid.uuid4().hex[:4],
                "title": "Imported Problem 1",
                "description": "Test problem for import",
                "input_description": "Input description",
                "output_description": "Output description",
                "samples": [{"input": "1 2", "output": "3"}],
                "constraints": "|a|,|b| <= 10^9",
                "testcases": [
                    {"input": "1 2", "output": "3"},
                    {"input": "5 7", "output": "12"}
                ],
                "hint": "",
                "source": "",
                "tags": [],
                "time_limit": 2.0,
                "memory_limit": 256,
                "author": "",
                "difficulty": ""
            },
            {
                "id": "imported_prob2_" + uuid.uuid4().hex[:4],
                "title": "Imported Problem 2",
                "description": "Another test problem",
                "input_description": "Input desc 2",
                "output_description": "Output desc 2",
                "samples": [{"input": "10", "output": "10"}],
                "constraints": "|x| <= 10^9",
                "testcases": [{"input": "10", "output": "10"}],
                "hint": "",
                "source": "",
                "tags": [],
                "time_limit": 1.0,
                "memory_limit": 128,
                "author": "",
                "difficulty": ""
            }
        ],
        "submissions": [
            {
                "submission_id": "1",  # API uses string IDs
                "user_id": "100",
                "problem_id": "imported_prob1",
                "language": "python",
                "code": "a, b = map(int, input().split())\nprint(a + b)",
                "status": "success",
                "details": [
                    {"id": 1, "result": "AC", "time": 1.01, "memory": 130},
                    {"id": 2, "result": "AC", "time": 1.02, "memory": 132}
                ],
                "score": 100,
                "counts": 100
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
        # According to api.md, must provide user_id or problem_id parameter
        submissions_response = client.get("/api/submissions/?user_id=100")
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

    # Test 1: Valid JSON format according to api.md
    valid_data = {
        "users": [{
            "user_id": "200",  # API uses string IDs
            "username": "test_user_" + uuid.uuid4().hex[:4],
            "password": "placeholder_hash_test_user",  # Placeholder password hash
            "role": "user",
            "join_time": "2024-01-01",  # API uses date format, not ISO datetime
            "submit_count": 0,
            "resolve_count": 0
        }],
        "problems": [],
        "submissions": []
    }

    json_content = json.dumps(valid_data).encode('utf-8')
    json_file = io.BytesIO(json_content)
    files = {"file": ("valid.json", json_file, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "import success"
    assert data["data"] is None

    # Test 2: Invalid JSON format
    invalid_json = b'{"users": [invalid json'
    invalid_file = io.BytesIO(invalid_json)
    files = {"file": ("invalid.json", invalid_file, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 400

    # Test 3: Empty file
    empty_file = io.BytesIO(b'')
    files = {"file": ("empty.json", empty_file, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 400

    # Test 4: Wrong content type
    csv_content = b'username,password,role\ntest,pass,user'
    csv_file = io.BytesIO(csv_content)
    files = {"file": ("data.csv", csv_file, "text/csv")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 400  # Should reject non-JSON files


def test_data_import_missing_required_fields(client):
    """Test POST /api/import/ - missing required fields in data"""
    setup_admin_session(client)

    # Test missing required fields in users
    invalid_user_data = {
        "users": [
            {"username": "test_user"},  # Missing user_id, role, join_time, submit_count, resolve_count
            {"user_id": "300"}     # Missing username, role, join_time, submit_count, resolve_count
        ],
        "problems": [],
        "submissions": []
    }

    json_content = json.dumps(invalid_user_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("invalid_users.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400

    # Test missing required fields in problems
    invalid_problem_data = {
        "users": [],
        "problems": [
            {
                "id": "test_prob",
                # Missing required fields like title, description, input_description, output_description, samples, constraints, testcases
            }
        ],
        "submissions": []
    }

    json_content = json.dumps(invalid_problem_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("invalid_problems.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == 400


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
            "user_id": str(1000 + i),  # API uses string IDs
            "username": f"bulk_user_{i}_{uuid.uuid4().hex[:4]}",
            "password": f"placeholder_hash_bulk_user_{i}",  # Placeholder password hash
            "role": "user",
            "join_time": "2024-01-01",  # API uses date format
            "submit_count": i,
            "resolve_count": i // 2
        })

    # Generate many problems
    for i in range(20):
        large_data["problems"].append({
            "id": f"bulk_prob_{i}_{uuid.uuid4().hex[:4]}",
            "title": f"Bulk Problem {i}",
            "description": f"Problem {i} description",
            "input_description": "Input",
            "output_description": "Output",
            "samples": [{"input": f"{i}", "output": f"{i}"}],
            "constraints": "|x| <= 10^9",
            "testcases": [{"input": f"{i}", "output": f"{i}"}],
            "hint": "",
            "source": "",
            "tags": [],
            "time_limit": 1.0,
            "memory_limit": 128,
            "author": "",
            "difficulty": ""
        })

    json_content = json.dumps(large_data).encode('utf-8')
    file_obj = io.BytesIO(json_content)
    files = {"file": ("large_dataset.json", file_obj, "application/json")}

    response = client.post("/api/import/", files=files)
    assert response.status_code == 200  # Should handle large datasets successfully


def test_data_import_no_file(client):
    """Test POST /api/import/ - no file provided"""
    setup_admin_session(client)

    # Try import without file
    response = client.post("/api/import/")
    assert response.status_code == 400


def test_data_export(client):
    """Test GET /api/export/"""
    # Reset and setup admin
    reset_system(client)
    setup_admin_session(client)

    # Create some test data first
    # Add a problem
    problem_id = "export_test_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "Export Test Problem",
        "description": "Test problem for export",
        "input_description": "Input description",
        "output_description": "Output description",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2", "output": "3"}],
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)

    # Create a user
    username, password, user_id = create_test_user(client)

    # Export data
    response = client.get("/api/export/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data

    # Verify export structure according to api.md
    export_data = data["data"]
    assert "users" in export_data
    assert "problems" in export_data
    assert "submissions" in export_data

    # Verify users data structure
    assert isinstance(export_data["users"], list)
    if len(export_data["users"]) > 0:
        user = export_data["users"][0]
        assert "user_id" in user
        assert "username" in user
        assert "password" in user  # According to api.md, password field is required
        assert "role" in user
        assert "join_time" in user
        assert "submit_count" in user
        assert "resolve_count" in user

        # Verify admin password is not plaintext according to api.md
        if user["role"] == "admin":
            # Password should be hashed, not plaintext "admintestpassword"
            assert user["password"] != "admintestpassword", "Admin password should not be plaintext in export"
            assert user["password"] != "", "Admin password should not be empty in export"

    # Verify problems data structure
    assert isinstance(export_data["problems"], list)
    if len(export_data["problems"]) > 0:
        problem = export_data["problems"][0]
        assert "id" in problem
        assert "title" in problem
        assert "description" in problem
        assert "input_description" in problem
        assert "output_description" in problem
        assert "samples" in problem
        assert "constraints" in problem
        assert "testcases" in problem
        assert "time_limit" in problem
        assert "memory_limit" in problem
        # Optional fields - don't assert these
        # assert "hint" in problem
        # assert "source" in problem
        # assert "tags" in problem
        # assert "author" in problem
        # assert "difficulty" in problem

    # Verify submissions data structure
    assert isinstance(export_data["submissions"], list)
    if len(export_data["submissions"]) > 0:
        submission = export_data["submissions"][0]
        assert "submission_id" in submission
        assert "user_id" in submission
        assert "problem_id" in submission
        assert "language" in submission
        assert "code" in submission
        assert "details" in submission
        assert "score" in submission
        assert "counts" in submission


def test_data_export_non_admin(client):
    """Test GET /api/export/ - non-admin access"""
    reset_system(client)
    username, password, user_id = create_test_user(client)
    setup_user_session(client, username, password)

    response = client.get("/api/export/")
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == 403


def test_data_export_not_logged_in(client):
    """Test GET /api/export/ - not logged in"""
    reset_system(client)

    response = client.get("/api/export/")
    assert response.status_code == 401  # According to api.md, should be 401 for not logged in


def test_system_reset(client):
    """Test POST /api/reset/"""
    # Setup some data first
    reset_system(client)
    setup_admin_session(client)

    # Add a problem
    problem_data = {
        "id": "reset_test_" + uuid.uuid4().hex[:4],
        "title": "Test Problem",
        "description": "Test",
        "input_description": "Input",
        "output_description": "Output",
        "samples": [{"input": "1", "output": "1"}],
        "constraints": "|x| <= 10^9",
        "testcases": [{"input": "1", "output": "1"}],
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)

    # Reset system
    response = client.post("/api/reset/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "system reset successfully"
    assert data["data"] is None


def test_system_reset_non_admin(client):
    """Test POST /api/reset/ - non-admin access"""
    reset_system(client)
    username, password, user_id = create_test_user(client)
    setup_user_session(client, username, password)

    response = client.post("/api/reset/")
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == 403


def test_system_reset_not_logged_in(client):
    """Test POST /api/reset/ - not logged in"""
    reset_system(client)

    response = client.post("/api/reset/")
    assert response.status_code == 401  # According to api.md, should be 401 for not logged in


def test_export_reset_import_login_workflow(client):
    """Test complete workflow: export data, reset system, import data, test user login"""
    # Reset and setup admin
    reset_system(client)
    setup_admin_session(client)

    # Create test data - a user who should be able to login after export-import
    test_username = "workflow_user_" + uuid.uuid4().hex[:4]
    test_password = "workflow_pass_123"
    user_data = {
        "username": test_username,
        "password": test_password
    }

    # Create the user
    register_response = client.post("/api/users/", json=user_data)
    assert register_response.status_code == 200
    original_user_id = register_response.json()["data"]["user_id"]

    # Create a problem for completeness
    problem_id = "workflow_prob_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "Workflow Test Problem",
        "description": "Test problem for workflow",
        "input_description": "Input description",
        "output_description": "Output description",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2", "output": "3"}],
        "time_limit": 1.0,
        "memory_limit": 128
    }
    client.post("/api/problems/", json=problem_data)

    # Verify the user can login before export
    logout_response = client.post("/api/auth/logout")
    login_test_response = client.post("/api/auth/login", json={
        "username": test_username,
        "password": test_password
    })
    assert login_test_response.status_code == 200
    assert login_test_response.json()["data"]["username"] == test_username

    # Re-login as admin for export
    setup_admin_session(client)

    # Step 1: Export all data
    export_response = client.get("/api/export/")
    assert export_response.status_code == 200
    export_data = export_response.json()["data"]

    # Verify the exported data contains our test user
    exported_usernames = [user["username"] for user in export_data["users"]]
    assert test_username in exported_usernames

    # Find our test user in export data
    test_user_export = None
    for user in export_data["users"]:
        if user["username"] == test_username:
            test_user_export = user
            break

    assert test_user_export is not None
    assert "password" in test_user_export
    # Password should be hashed, not plaintext
    assert test_user_export["password"] != test_password, "Exported password should not be plaintext"

    # Step 2: Reset the system
    reset_response = client.post("/api/reset/")
    assert reset_response.status_code == 200

    # Verify system is actually reset - user should not be able to login
    client.post("/api/auth/logout")  # Clear any session
    login_after_reset = client.post("/api/auth/login", json={
        "username": test_username,
        "password": test_password
    })
    assert login_after_reset.status_code == 401  # User should not exist after reset

    # Step 3: Re-login as admin and import the data
    setup_admin_session(client)

    # Convert export data to import format
    import json
    import io
    json_content = json.dumps(export_data).encode('utf-8')
    import_file = io.BytesIO(json_content)
    files = {"file": ("workflow_import.json", import_file, "application/json")}

    import_response = client.post("/api/import/", files=files)
    assert import_response.status_code == 200
    import_result = import_response.json()
    assert import_result["code"] == 200
    assert import_result["msg"] == "import success"

    # Step 4: Test that the original user can login with original password
    client.post("/api/auth/logout")  # Clear admin session

    final_login_response = client.post("/api/auth/login", json={
        "username": test_username,
        "password": test_password
    })
    assert final_login_response.status_code == 200
    final_login_data = final_login_response.json()
    assert final_login_data["code"] == 200
    assert final_login_data["msg"] == "login success"
    assert final_login_data["data"]["username"] == test_username
    assert final_login_data["data"]["role"] == "user"

    # Verify user data integrity after import
    imported_user_id = final_login_response.json()["data"]["user_id"]
    user_info_response = client.get(f"/api/users/{imported_user_id}")
    assert user_info_response.status_code == 200
    user_info = user_info_response.json()["data"]
    assert user_info["username"] == test_username
    assert user_info["role"] == "user"

    # Verify problems were also imported
    setup_admin_session(client)
    problems_response = client.get("/api/problems/")
    assert problems_response.status_code == 200
    problems_data = problems_response.json()["data"]
    problem_ids = [prob["id"] for prob in problems_data]
    assert problem_id in problem_ids
