# ODM

## Introduction

This module is build top of pymongo and pydantic. The purpose of this module is to do provide easy access to the database with the python object feature with MongoDB and pymongo. With pymongo there was no way to validate data before create or update a document and very easy to make spelling mistakes of a collection name when you are doing database operation. This module provides you minimal ODM with a modeling feature so that you don’t have to look up the MongoDB dashboard(Mongo Compass) to know about field names or data types.

This module does not compromise performance since it’s not serializing a list of objects. As like pymongo this odm has all minimal method as like pymongo. And it should support all minimal functionality. Please contribute if you fill some functionality is missin.

## Documentation

- Define a User model.
```py
from datetime import datetime
from app.odm.models import Document
from pydantic import Field
from typing import Optional

class User(Document):
    password: str = Field(...)
    email: str = Field(...)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    is_active: bool = True
    image: Optional[str] = Field(default=None)

    date_joined: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection_name = "user"
```