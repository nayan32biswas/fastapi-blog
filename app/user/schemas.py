from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class MinimalUser(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image: Optional[str] = ""

    class Config:
        orm_mode = True
