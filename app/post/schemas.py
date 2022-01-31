from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.base.types import ObjectIdStr
from app.user.schemas import MinimalUser


class BaseComment(BaseModel):
    content: str


class CommentOut(BaseComment):
    id: ObjectIdStr
    timestamp: datetime
    user: MinimalUser

    class Config:
        orm_mode = True


class BasePost(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    published_at: Optional[datetime] = None
    is_publish: Optional[bool] = False
    image: Optional[str] = ""


class PostForm(BasePost):
    content: str


class PostListOut(BasePost):
    id: ObjectIdStr

    class Config:
        orm_mode = True


class PostDetailsOut(BasePost):
    id: ObjectIdStr
    content: str
    comments: List[CommentOut]
    user: MinimalUser

    class Config:
        orm_mode = True
