import uuid
import time
import pytest
from test_helpers import setup_admin_session, setup_user_session


def test_submit_solution(client):
    """Test POST /api/submissions/"""
    # Set up admin session
    setup_admin_session(client)

    problem_id = "test_submit_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "加法题",
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

    # Create user via API
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": user, "password": upw}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, user, upw)

    # Submit solution
    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }

    response = client.post("/api/submissions/", json=submission_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert "submission_id" in data["data"]
    assert data["data"]["status"] == "pending"

    # Test invalid problem_id
    submission_data["problem_id"] = "nonexistent"
    response = client.post("/api/submissions/", json=submission_data)
    assert response.status_code == 404


def test_get_submission_result(client):
    """Test GET /api/submissions/{submission_id}"""
    # Set up admin session
    setup_admin_session(client)

    problem_id = "test_result_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "测试结果",
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

    # Create user and submit
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": user, "password": upw}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, user, upw)

    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }

    submit_response = client.post("/api/submissions/", json=submission_data)
    submission_id = submit_response.json()["data"]["submission_id"]

    # Wait for judging
    time.sleep(1)

    # Get submission result
    response = client.get(f"/api/submissions/{submission_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert "score" in data["data"]
    assert "counts" in data["data"]

    # Assert specific expected values based on test case
    # Problem has 1 test case, each worth 10 points, correct solution should get full score
    assert data["data"]["score"] == 10  # 1 test case × 10 points
    assert data["data"]["counts"] == 10  # Total possible points


def test_get_submissions_list(client):
    """Test GET /api/submissions/"""
    # Set up admin session
    setup_admin_session(client)

    problem_id = "test_list_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "测试列表",
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

    # Create user and submit
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": user, "password": upw}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, user, upw)

    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }

    client.post("/api/submissions/", json=submission_data)

    # Get submissions list - must provide user_id or problem_id according to api.md
    # Test with problem_id (one of the required primary conditions)
    response = client.get(f"/api/submissions/?problem_id={problem_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert "total" in data["data"]
    assert "submissions" in data["data"]
    assert isinstance(data["data"]["submissions"], list)

    # Test without primary parameters should fail (400 error)
    response = client.get("/api/submissions/")
    assert response.status_code == 400  # Should require user_id or problem_id


def test_rejudge_submission(client):
    """Test PUT /api/submissions/{submission_id}/rejudge"""
    # Set up admin session
    setup_admin_session(client)

    problem_id = "test_rejudge_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "重新评测",
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

    # Create user and submit
    user = "user_" + uuid.uuid4().hex[:8]
    upw = "pw_" + uuid.uuid4().hex[:8]
    user_data = {"username": user, "password": upw}
    client.post("/api/users/", json=user_data)
    setup_user_session(client, user, upw)

    submission_data = {
        "problem_id": problem_id,
        "language": "python",
        "code": "a, b = map(int, input().split())\nprint(a + b)"
    }

    submit_response = client.post("/api/submissions/", json=submission_data)
    submission_id = submit_response.json()["data"]["submission_id"]

    # Switch to admin session for rejudge
    setup_admin_session(client)

    # Rejudge submission
    response = client.put(f"/api/submissions/{submission_id}/rejudge")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "rejudge started"
    assert data["data"]["submission_id"] == submission_id
    assert data["data"]["status"] == "pending"

    # Test non-existent submission
    response = client.put("/api/submissions/999999/rejudge")
    assert response.status_code == 404