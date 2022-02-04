from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    EnumField,
    StringField,
)

from .permission import PermissionType


class Permission(EmbeddedDocument):
    type = EnumField(PermissionType, default=PermissionType.OTHER)
    # value should store one or multiple char of "CRUD" Create, Retrieve, Update, Delete permission
    value = StringField(max_length=8, required=True)


class PermissionGroup(Document):
    name = StringField(max_length=256, required=True, unique=True)
    description = StringField()
    permissions = EmbeddedDocumentListField(Permission)
