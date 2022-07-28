from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.odm.types import ObjectIdStr

from app.user.schemas import MinimalUser


class EmbedeComment(BaseModel):
    id: ObjectIdStr = Field(alias="_id")
    user: MinimalUser
    description: str
    created_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class BaseComment(BaseModel):
    description: str


class CommentOut(BaseComment):
    id: ObjectIdStr = Field(alias="_id")
    user: MinimalUser
    childs: Optional[List[EmbedeComment]]
    created_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class BasePost(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    published_at: Optional[datetime] = None
    is_publish: Optional[bool] = False
    image: Optional[str] = ""


class PostForm(BasePost):
    description: str


class PostListOut(BasePost):
    id: ObjectIdStr = Field(alias="_id")
    user: MinimalUser

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class PostDetailsOut(BasePost):
    id: ObjectIdStr = Field(alias="_id")
    description: str
    comments: Optional[List[CommentOut]]
    # user: MinimalUser

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
