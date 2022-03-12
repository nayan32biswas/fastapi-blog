from fastapi.testclient import TestClient
from fastapi import status
from app.main import app


client = TestClient(app)


def test_get_me():
    request = client.get("/api/v1/me")
    assert request.status_code == status.HTTP_401_UNAUTHORIZED
