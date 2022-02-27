from typing import Optional, List
from pydantic import BaseModel

from app.odm.models import ObjectIdStr
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
    active: bool = True
    description: Optional[str] = None
    permissions: List[PermissionIn]


class PermissionDataType(BaseModel):
    type: str
    value: str

    class Config:
        orm_mode = True


class PermissionGroupOut(BaseModel):
    id: Optional[ObjectIdStr] = None
    name: str
    active: bool = False
    description: Optional[str] = None
    permissions: List[PermissionDataType]

    class Config:
        orm_mode = True


class UsersIn(BaseModel):
    user_ids: List[str]
