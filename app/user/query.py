from .schema import UserInDB

from ..db import fake_users_db


def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
