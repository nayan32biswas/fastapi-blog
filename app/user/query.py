from .schemas import UserInDB

from .models import User


def get_user(username: str):
    user = User.objects(username=username).first()
    if user:
        return UserInDB(**user.to_mongo())
