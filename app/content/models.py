from datetime import datetime
from typing import Optional

from pydantic import Field

from app.base.models import Document
from app.base.types import PydanticObjectId


class Content(Document):
    added_by_id: PydanticObjectId = Field(...)
    name: str = Field(..., max_length=255)
    image: Optional[str] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)
    is_publish: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        NAME = "content"
        allow_inheritance = True


class Course(Document):
    content_id: PydanticObjectId = Field(...)
    description: str = Field(...)

    class Config:
        demo = "course"


class Article(Document):
    content_id: PydanticObjectId = Field(...)
    description: str = Field(...)
