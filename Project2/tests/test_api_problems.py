import uuid

from test_helpers import setup_user_session, reset_system, create_test_user


def test_get_problems_list(client):
    """Test GET /api/problems/"""
    # Get problems list (public endpoint)
    response = client.get("/api/problems/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)


def test_add_problem(client):
    """Test POST /api/problems/ - authenticated users can add problems"""
    # Reset system
    reset_system(client)

    # Test admin user can add problem (using default admin session)
    # Add problem
    problem_data = {
        "id": "test_sum_" + uuid.uuid4().hex[:4],
        "title": "两数之和",
        "description": "输入两个整数，输出它们的和。",
        "input_description": "输入为一行，包含两个整数。",
        "output_description": "输出这两个整数的和。",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [
            {"input": "1 2", "output": "3"},
            {"input": "10 20", "output": "30"}
        ],
        "time_limit": 1.0,
        "memory_limit": 128,
        "hint": "有负数哦！",
        "source": "测试来源",
        "tags": ["基础题"],
        "author": "测试作者",
        "difficulty": "入门"
    }

    response = client.post("/api/problems/", json=problem_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "add success"
    assert "data" in data
    assert "id" in data["data"]

    # Test that regular users can now add problems
    # Create regular user via API
    username, password, user_id = create_test_user(client)

    # Set up user session (not admin)
    setup_user_session(client, username, password)

    # Change problem ID to avoid conflicts
    problem_data["id"] = "test_user_" + uuid.uuid4().hex[:4]

    response = client.post("/api/problems/", json=problem_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "add success"
    assert "data" in data
    assert "id" in data["data"]


def test_get_problem_info(client):
    """Test GET /api/problems/{problem_id}"""
    # Reset system
    reset_system(client)

    problem_id = "test_problem_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "测试题目",
        "description": "这是一个测试题目",
        "input_description": "输入描述",
        "output_description": "输出描述",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2", "output": "3"}],
        "time_limit": 1.0,
        "memory_limit": 128,
        "hint": "测试提示",
        "source": "测试来源",
        "tags": ["测试标签"],
        "author": "测试作者",
        "difficulty": "入门"
    }

    client.post("/api/problems/", json=problem_data)

    # Get problem info
    response = client.get(f"/api/problems/{problem_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert data["data"]["id"] == problem_id
    assert data["data"]["title"] == "测试题目"

    # Test non-existent problem
    response = client.get("/api/problems/nonexistent")
    assert response.status_code == 404


def test_delete_problem(client):
    """Test DELETE /api/problems/{problem_id}"""
    # Reset system
    reset_system(client)

    problem_id = "test_delete_" + uuid.uuid4().hex[:4]
    problem_data = {
        "id": problem_id,
        "title": "待删除题目",
        "description": "这是一个待删除的题目",
        "input_description": "输入描述",
        "output_description": "输出描述",
        "samples": [{"input": "1 2", "output": "3"}],
        "constraints": "|a|,|b| <= 10^9",
        "testcases": [{"input": "1 2", "output": "3"}],
        "time_limit": 1.0,
        "memory_limit": 128,
        "hint": "测试提示",
        "source": "测试来源",
        "tags": ["测试标签"],
        "author": "测试作者",
        "difficulty": "入门"
    }

    client.post("/api/problems/", json=problem_data)

    # Delete problem
    response = client.delete(f"/api/problems/{problem_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "delete success"
    assert data["data"]["id"] == problem_id

    # Verify problem is deleted
    response = client.get(f"/api/problems/{problem_id}")
    assert response.status_code == 404

    # Test non-existent problem
    response = client.delete("/api/problems/nonexistent")
    assert response.status_code == 404