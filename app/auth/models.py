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


def get_filtered_auth(permission_list, permission_type: PermissionType):
    return [data["type"] == permission_type for data in permission_list]


def get_permissions(permission_type=PermissionType.POST):

    r = RedisHelper(key=authentication_key)
    permission_list = r.get_data()
    print(permission_list)
    if permission_list:
        return get_filtered_auth(permission_list, permission_type)

    permissions = []
    # for permission_group in PermissionGroup.objects(active=True):
    for permission_group in PermissionGroup.objects():
        permissions += [
            {"type": permission.type, "value": permission.value}
            for permission in permission_group.permissions
        ]

    # r.data = permissions
    # r.set_data()
    return get_filtered_auth(permissions, permission_type)
