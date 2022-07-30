from fastapi.testclient import TestClient

from app.main import app
from app.test.config import get_header, get_token, test_email, init_config  # noqa
from app.user.models import User

client = TestClient(app)


def test_admin_token():
    access_token = get_token()
    assert type(access_token) == str


# def test_user_info_v3():
#     response = client.get("/api/v3/divethru/user/info", headers=get_header())
#     assert response.status_code == 200
#     assert response.json()["email"] == test_email


# def test_user_info_update_v3():
#     payload = {"first_name": "Test", "last_name": "User"}
#     response = client.put(
#         "/api/v1/divethru/user/info", json=payload, headers=get_header()
#     )
#     assert response.status_code == 200
#     user = User.get_one({"email": test_email})
#     if user is None:
#         raise Exception("Invalid user")
#     assert user.first_name == payload["first_name"]
#     assert user.last_name == payload["last_name"]
