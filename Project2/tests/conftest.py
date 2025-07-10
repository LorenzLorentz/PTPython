import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c
