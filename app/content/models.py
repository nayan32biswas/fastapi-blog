from datetime import datetime
from typing import Optional

from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.odm.models import Document, PydanticDBRef
from app.odm.models import PydanticObjectId


class Content(Document):
    added_by_id: PydanticObjectId = Field(...)
    name: str = Field(..., max_length=255)
    image: Optional[str] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)
    is_publish: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection_name = "content"
        allow_inheritance = True
        indexes = (
            IndexModel([("added_by_id", ASCENDING)]),
            IndexModel([("name", ASCENDING)], background=True, sparse=True),
        )


class Course(Content):
    title: str = Field(max_length=100)
    description: str = Field(...)

    class Config:
        demo = "course"
        indexes = (IndexModel([("title", ASCENDING)], unique=True),)


class Article(Document):
    content: PydanticDBRef = Field(...)
    description: str = Field(...)
