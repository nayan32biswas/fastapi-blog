from enum import Enum


class UserRoles(str, Enum):
    ADMIN = "ADMIN"  # Super user have all access
    STAFF = "STAFF"  # Company staff user
    INSTRUCTOR = "INSTRUCTOR"  # Has permission to login into dashboard
    BASIC = "BASIC"  # Basic User


class PermissionType(str, Enum):
    POST = "POST"
    USER = "USER"
    SUPPORT = "SUPPORT"
    PAYMENT = "PAYMENT"
    OTHER = "OTHER"


class PermissionValueChar(str, Enum):
    CREATE = "C"
    RETRIEVE = "R"
    UPDATE = "U"
    DELETE = "D"


def has_create_perm(value: str) -> bool:
    return PermissionValueChar.CREATE in value


def has_retrive_perm(value: str) -> bool:
    return PermissionValueChar.RETRIEVE in value


def has_update_perm(value: str) -> bool:
    return PermissionValueChar.UPDATE in value


def has_delete_perm(value: str) -> bool:
    return PermissionValueChar.DELETE in value
