from datetime import timedelta
from typing import List, Optional

from pydantic import BaseModel, Field

from app.base.models import Document
from app.base.utils.local_cache import RedisHelper
from .permission import PermissionType, PermissionValueChar


class Permission(BaseModel):
    type: PermissionType = PermissionType.OTHER
    # value should store one or multiple char of "CRUD" Create, Retrieve, Update, Delete permission
    value: str = PermissionValueChar.RETRIEVE.value


class PermissionGroup(Document):
    active: bool = True
    name: str = Field(...)
    description: Optional[str]
    permissions: List[Permission] = []

    class Config:
        NAME = "permission_group"


authentication_key = "local:auth:permissions"


def remove_permissions_cache():
    r = RedisHelper(key=authentication_key)
    r.delete_data()


def _get_filtered_auth(
    permission_list, user_perm_group_ids, permission_type: PermissionType
):
    user_perm_group_ids = [str(id) for id in user_perm_group_ids]
    return [
        data
        for data in permission_list
        if data["type"] == permission_type and data["group_id"] in user_perm_group_ids
    ]


def get_cached_or_db_permissions(
    user_perm_group_ids=[], permission_type=PermissionType.POST
):
    r = RedisHelper(key=authentication_key)
    permission_list = r.get_data()
    if permission_list:
        return _get_filtered_auth(permission_list, user_perm_group_ids, permission_type)

    permissions = []
    # for permission_group in PermissionGroup.objects(active=True):
    raise NotImplementedError()
    for permission_group in PermissionGroup.objects():
        permissions += [
            {
                "type": permission.type,
                "value": permission.value,
                "group_id": str(permission_group.id),
            }
            for permission in permission_group.permissions
        ]
    r.data = permissions
    r.set_data(time=timedelta(days=1))
    return _get_filtered_auth(permissions, user_perm_group_ids, permission_type)
