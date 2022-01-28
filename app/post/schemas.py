from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BasePost(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    published_at: Optional[datetime] = None
    is_publish: Optional[bool] = False


class PostForm(BasePost):
    content: str


class PostOut(PostForm):
    id: Optional[str] = None

    class Config:
        orm_mode = True
