import uuid
import pytest
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user


def test_register_language(client):
    """Test POST /api/languages/"""
    # Reset storage to ensure test isolation
    reset_system(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Register new language
    language_data = {
        "name": "go_" + uuid.uuid4().hex[:4],
        "file_ext": ".go",
        "compile_cmd": "go build -o main main.go",
        "run_cmd": "./main"
    }
    
    response = client.post("/api/languages/", json=language_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "language registered"
    assert data["data"]["name"] == language_data["name"]
    
    # Test language without compile command (interpreted language)
    script_language_data = {
        "name": "ruby_" + uuid.uuid4().hex[:4],
        "file_ext": ".rb",
        "run_cmd": "ruby main.rb"
    }
    
    response = client.post("/api/languages/", json=script_language_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "language registered"
    assert data["data"]["name"] == script_language_data["name"]
    
    # Test duplicate language name
    response = client.post("/api/languages/", json=language_data)
    assert response.status_code == 400
    
    # Test missing required fields
    invalid_data = {"name": "invalid_lang"}  # Missing run_cmd
    response = client.post("/api/languages/", json=invalid_data)
    assert response.status_code == 400
    
    # Test non-admin access
    username, password, user_id = create_test_user(client)
    setup_user_session(client, username, password)
    
    new_language_data = {
        "name": "rust_" + uuid.uuid4().hex[:4],
        "file_ext": ".rs",
        "compile_cmd": "rustc main.rs",
        "run_cmd": "./main"
    }
    
    response = client.post("/api/languages/", json=new_language_data)
    assert response.status_code == 403


def test_get_supported_languages(client):
    """Test GET /api/languages/"""
    # Reset storage to ensure test isolation
    reset_system(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Set up admin session
    setup_admin_session(client)
    
    # Register test languages
    languages = [
        {
            "name": "cpp_" + uuid.uuid4().hex[:4],
            "file_ext": ".cpp",
            "compile_cmd": "g++ -o main main.cpp",
            "run_cmd": "./main"
        },
        {
            "name": "java_" + uuid.uuid4().hex[:4],
            "file_ext": ".java",
            "compile_cmd": "javac Main.java",
            "run_cmd": "java Main"
        },
        {
            "name": "node_" + uuid.uuid4().hex[:4],
            "file_ext": ".js",
            "run_cmd": "node main.js"
        }
    ]
    
    registered_names = []
    for lang in languages:
        response = client.post("/api/languages/", json=lang)
        if response.status_code == 200:
            registered_names.append(lang["name"])
    
    # Get supported languages list
    response = client.get("/api/languages/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["msg"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)
    
    # Verify structure of language entries
    for lang_info in data["data"]:
        assert "name" in lang_info
        assert "run_cmd" in lang_info
        # compile_cmd is optional
    
    # Check that our registered languages are in the list
    returned_names = [lang["name"] for lang in data["data"]]
    for name in registered_names:
        assert name in returned_names
    
    # Test that regular users can also get languages list (it's a public endpoint)
    username, password, user_id = create_test_user(client)
    setup_user_session(client, username, password)
    
    response = client.get("/api/languages/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200