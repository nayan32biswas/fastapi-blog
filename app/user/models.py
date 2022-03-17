from datetime import datetime
from typing import List, Optional

from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.odm.models import Document
from app.odm.models import ObjectIdStr
from ..auth.permission import UserRoles


class User(Document):
    username: str = Field(...)
    email: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)

    is_active: bool = True
    date_joined: datetime = Field(default_factory=datetime.utcnow)
    role: UserRoles = Field(default=UserRoles.BASIC)
    # store all permission_group id and get permissions from local cache data.
    permissions: List[ObjectIdStr] = []

    last_login: datetime = Field(default_factory=datetime.utcnow)
    password: str = Field(...)
    image: Optional[str] = Field(default=None)

    class Config:
        collection_name = "user"
        indexes = (
            IndexModel([("username", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("last_login", ASCENDING)]),
            IndexModel(
                [("first_name", ASCENDING), ("last_name", ASCENDING)],
                unique=True,
            ),
        )


# class EmbeddedUser(EmbeddedDocument):
#     user_id = ObjectIdField()
#     username = StringField(max_length=150, required=True)
#     image_url = StringField()
