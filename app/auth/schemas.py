from typing import Optional, List
from pydantic import BaseModel, Field

from app.odm.types import ObjectIdStr
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
    id: ObjectIdStr = Field(alias="_id")
    name: str
    active: bool = False
    description: Optional[str] = None
    permissions: List[PermissionDataType]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class UsersIn(BaseModel):
    user_ids: List[str]
