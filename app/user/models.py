from datetime import datetime
from typing import List, Optional

from pydantic import Field

from app.base.models import DBBaseModel
from app.base.types import ObjectIdStr
from app.base.utils.decorator import staticproperty
from ..auth.permission import UserRoles


class User(DBBaseModel):
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

    class Meta:
        NAME = "user"

    @staticproperty
    def _db() -> str:
        return User.Meta.NAME


# class EmbeddedUser(EmbeddedDocument):
#     user_id = ObjectIdField()
#     username = StringField(max_length=150, required=True)
#     image_url = StringField()
