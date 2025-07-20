import uuid
import time
import pytest
import json
import io
from test_helpers import setup_admin_session, setup_user_session, reset_system

def test_get_submission_result(client):
    """Test GET /api/submissions/{submission_id}"""
    reset_system(client)
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

    spj_code = """
import sys

def main():
    if len(sys.argv) != 4:
        sys.stderr.write("SPJ Internal Error: Incorrect number of arguments.\n")
        sys.exit(2)

    input_file (sys.argv[1])
    user_output_file = sys.argv[2]
    answer_file = sys.argv[3]

    try:
        with open(user_output_file, 'r') as f:
            user_content = f.read().strip()

        with open(answer_file, 'r') as f:
            answer_content = f.read().strip()

    except IOError as e:
        sys.stderr.write(f"SPJ Internal Error: Cannot read files. {e}\n")
        sys.exit(2)
    
    if user_content == answer_content:
        sys.exit(0)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
"""

    file_obj = io.BytesIO(spj_code.encode('utf-8'))
    files = {"file": ("spj.py", file_obj)}
    response = client.post(f"/api/problems/{problem_id}/spj", files=files)
    with open("error.log","a") as f:
        print(response, response.json(), file=f)

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
    time.sleep(10)

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

    # Test non-existent submission
    response = client.get("/api/submissions/999999")
    assert response.status_code == 404