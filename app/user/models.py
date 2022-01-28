from enum import Enum
from datetime import datetime

from mongoengine import Document, StringField, DateTimeField, EmailField, BooleanField
from mongoengine import EnumField


class UserRoles(Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    BASIC = "BASIC"


class User(Document):
    username = StringField(max_length=150, required=True, unique=True)
    email = EmailField(max_length=150, required=True, unique=True)
    first_name = StringField(max_length=150)
    last_name = StringField(max_length=150)

    is_active = BooleanField(default=True)
    date_joined = DateTimeField(default=datetime.utcnow)
    role = EnumField(UserRoles, default=UserRoles.BASIC)

    last_login = DateTimeField(default=datetime.utcnow)
    password = StringField(max_length=128)