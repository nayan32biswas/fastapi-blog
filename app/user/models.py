from datetime import datetime

from mongoengine import (
    BooleanField,
    Document,
    DateTimeField,
    EmailField,
    EnumField,
    SortedListField,
    ObjectIdField,
    StringField,
)

from ..auth.permission import UserRoles


class User(Document):
    username = StringField(max_length=150, required=True, unique=True)
    email = EmailField(max_length=150, required=True, unique=True)
    first_name = StringField(max_length=150)
    last_name = StringField(max_length=150)

    is_active = BooleanField(default=True)
    date_joined = DateTimeField(default=datetime.utcnow)
    role = EnumField(UserRoles, default=UserRoles.BASIC)
    # store all permission_group id and get permissions from local cache data.
    permissions = SortedListField(ObjectIdField())

    last_login = DateTimeField(default=datetime.utcnow)
    password = StringField(max_length=128)
    image = StringField()


# class EmbeddedUser(EmbeddedDocument):
#     user_id = ObjectIdField()
#     username = StringField(max_length=150, required=True)
#     image_url = StringField()
