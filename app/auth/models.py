from datetime import timedelta
from mongoengine import (
    BooleanField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    EnumField,
    StringField,
)

from .permission import PermissionType
from app.base.local_cache import RedisHelper


class Permission(EmbeddedDocument):
    type = EnumField(PermissionType, default=PermissionType.OTHER)
    # value should store one or multiple char of "CRUD" Create, Retrieve, Update, Delete permission
    value = StringField(max_length=8, required=True)


class PermissionGroup(Document):
    active = BooleanField(required=True, default=True)
    name = StringField(max_length=256, required=True, unique=True)
    description = StringField()
    permissions = EmbeddedDocumentListField(Permission)


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
