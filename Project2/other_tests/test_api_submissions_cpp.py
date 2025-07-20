import uuid
import time
import pytest
from test_helpers import setup_admin_session, setup_user_session

def test_get_submission_result_cpp(client):
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
        "language": "cpp",
        "code": r'#include <stdio.h>\nint main(){int a,b;\nscanf("%d%d",&a,&b);\nprintf("%d",a+b);\nreturn 0;\n}'
    }

    submit_response = client.post("/api/submissions/", json=submission_data)
    submission_id = submit_response.json()["data"]["submission_id"]

    # Wait for judging
    time.sleep(5)