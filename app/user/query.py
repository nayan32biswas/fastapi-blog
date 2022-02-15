from typing import Optional
from app.base.types import ObjectIdStr

from .models import User


def get_user(
    db,
    id: Optional[ObjectIdStr] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
):
    query = []
    if id:
        query.append({"_id": id})
    if username:
        query.append({"username": username})
    if email:
        query.append({"email": email})
    user = db[User._db].find_one({"$or": query})
    if user:
        return User(**user)
    
    print(user)
    return None


def user_create(db):
    user_data = dict(
        username="333",
        email="333@gmail.com",
        first_name="333",
        last_name="333",
        password="12345",
    )
    user = User(**user_data)
    db[User._db].insert_one(user.dict())
    print("User created")
    return True
