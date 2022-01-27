from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from fastapi import File, UploadFile


class PostIn(BaseModel):
    name: str = Field(..., min_length=5, max_length=250)
    description: Optional[str] = None
    published_at: datetime = None
    number: int = 0


class PostOut(PostIn):
    id: int = None


class PostForm(PostIn):
    image: UploadFile = File(...)
