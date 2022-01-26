from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    name: str
    description: Optional[str] = None
    published_at: datetime = None
