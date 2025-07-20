import uuid
import pytest
import time
from test_helpers import setup_admin_session, setup_user_session, reset_system, create_test_user
from app.api.utils.data import seed_other_data
from app.db.database import SessionLocal

def test_plagiarism(client):
    """Test /api/plagiarism/"""
    # reset_system(client)
    reset_system(client)
    seed_other_data(SessionLocal())
    time.sleep(10)
    setup_admin_session(client)

    data = {
        "problem_id": "problem 1",
        "submission_id": 1,
        "threshold": 0.4
    }

    response = client.post("/api/plagiarism/", json=data)
    data = response.json()
    with open("error.log", "a") as f:
        print(data, file=f)

    time.sleep(2)

    response = client.get("/api/plagiarism/{}".format(data["data"]["task_id"]))
    with open("error.log", "a") as f:
        print(response.json(), file=f)

    response = client.get("/api/plagiarism/{}/report".format(data["data"]["task_id"]))
    with open("error.log", "a") as f:
        print(response.json(), file=f)