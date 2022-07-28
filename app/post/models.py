from datetime import datetime
from typing import List, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from app.odm.types import PydanticObjectId
from app.odm.models import Document


class Post(Document):
    user_id: PydanticObjectId = Field(...)

    name: str = Field(max_length=512)
    description: Optional[str] = None
    image: Optional[str] = None

    published_at: Optional[datetime] = None
    is_publish: bool = True

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmbeddedComment(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId)
    user_id: PydanticObjectId = Field(...)
    description: str = Field(...)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Comment(Document):
    user_id: PydanticObjectId = Field(...)
    post_id: PydanticObjectId = Field(...)
    childs: List[EmbeddedComment] = []

    description: str = Field(...)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
