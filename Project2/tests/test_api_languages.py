import uuid
import pytest
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user


def test_register_language(client):
    """Test POST /api/languages/"""
    # Reset storage to ensure test isolation
    reset_system(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Register C++ language
    language_data = {
        "name": "cpp",
        "file_ext": ".cpp",
        "compile_cmd": "g++ -o main main.cpp -std=c++17",
        "run_cmd": "./main"
    }
    
    response = client.post("/api/languages/", json=language_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "language registered"
    assert data["data"]["name"] == "cpp"
    
    # Test non-admin access
    username, password, user_id = create_test_user(client)
    setup_user_session(client, username, password)
    
    response = client.post("/api/languages/", json=language_data)
    assert response.status_code == 403


def test_get_supported_languages(client):
    """Test GET /api/languages/"""
    # Reset storage to ensure test isolation
    reset_system(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Register C++ language
    cpp_language = {
        "name": "cpp",
        "file_ext": ".cpp",
        "compile_cmd": "g++ -o main main.cpp -std=c++17",
        "run_cmd": "./main"
    }
    
    response = client.post("/api/languages/", json=cpp_language)
    assert response.status_code == 200
    
    # Get supported languages list
    response = client.get("/api/languages/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert isinstance(data["data"], dict)
    assert "name" in data["data"]
    assert isinstance(data["data"]["name"], list)