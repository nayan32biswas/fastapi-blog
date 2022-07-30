from functools import lru_cache
import os
from fastapi.testclient import TestClient
from pydantic import EmailStr
import pytest
from app.auth.permission import UserRoles
from app.auth.utils import get_password_hash

from app.base import config
from app.main import app
from app.odm.connection import connect, disconnect
from app.user.models import User

client = TestClient(app)

test_username = os.environ.get("TEST_USERNAME", "test")
test_email = os.environ.get("TEST_EMAIL", "test@test.com")
test_pass = os.environ.get("TEST_PASS", "testpass")


@lru_cache(maxsize=None)
def get_token():
    User.update_one({"email": test_email}, {"$inc": {"update_count": 1}})
    response = client.post(
        "/token", data={"username": test_username, "password": test_pass}
    )
    print(response.status_code)
    assert response.status_code == 200
    return response.json()["access_token"]


@lru_cache(maxsize=None)
def get_user():
    user = User.get_one({"email": test_email})
    if not user:
        user = User(username=test_username, email=EmailStr(test_email)).create()
    return user


@lru_cache(maxsize=None)
def get_header():
    token = get_token()
    return {
        "Authorization": f"Bearer {token}",
        "LOCAL-TIMEZONE": "Asia/Dhaka",
    }


@pytest.fixture(autouse=True)
def init_config():
    print("Initiate test info")

    connect(config.DB_URL)
    user = get_user()
    user.update(
        {"$set": {"role": UserRoles.ADMIN, "password": get_password_hash(test_pass)}}
    )

    yield None

    user.update({"$set": {"role": UserRoles.BASIC, "password": None}})

    disconnect()
    print("Clean everything")
