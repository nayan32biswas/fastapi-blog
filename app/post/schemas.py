from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.base.types import PydanticObjectId


class BasePost(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    published_at: Optional[datetime] = None
    is_publish: Optional[bool] = False
    image: Optional[str] = ""


class PostForm(BasePost):
    content: str


class PostListOut(BasePost):
    id: PydanticObjectId

    class Config:
        orm_mode = True


class PostDetailsOut(BasePost):
    id: PydanticObjectId
    content: str

    class Config:
        orm_mode = True
