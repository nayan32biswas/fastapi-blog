from .schemas import UserBase

from .models import User


def get_user(username: str):
    user = User.objects(username=username).first()
    if user:
        return UserBase(**user.to_mongo())
