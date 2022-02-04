from typing import Optional, List
from pydantic import BaseModel

from app.base.types import ObjectIdStr
from .permission import PermissionValueChar, PermissionType


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class PermissionIn(BaseModel):
    type: PermissionType
    value: List[PermissionValueChar]


class PermissionGroupIn(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[PermissionIn]


class PermissionOut(BaseModel):
    type: str
    value: str

    class Config:
        orm_mode = True


class PermissionGroupOut(BaseModel):
    id: ObjectIdStr
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut]

    class Config:
        orm_mode = True


class PermissionGroupUpdate(BaseModel):
    # id: ObjectIdStr
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
