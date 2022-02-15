from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.base.query import get_object_or_404
from app.user.models import User

from .schemas import (
    Token,
    UsersIn,
    PermissionGroupIn,
    PermissionGroupOut,
)
from .utils import authenticate_user, create_access_token
from .models import Permission, PermissionGroup, remove_permissions_cache

router = APIRouter()


@router.post("/token", response_model=Token)
# "localhost:8000/token" for validate OpenAPI
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Extend or reimplement OAuth2PasswordRequestForm to change authentication format or add additional fields
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


def get_validate_permission_group(data: PermissionGroupIn) -> dict:
    permissions = []
    unique_permissions = set()
    for permission in data.permissions:
        if permission.type not in unique_permissions:
            """Ensure that permission does not have duplicates"""
            unique_permissions.add(permission.type)
            value = "".join(sorted(set(permission.value)))
            permissions.append(Permission(type=permission.type, value=value))
    result = {
        "name": data.name,
        "active": data.active,
        "description": data.description,
        "permissions": permissions,
    }
    return result


@router.post("/api/v1/permission-group/")
def create_permission_group(data: PermissionGroupIn):
    permission_group = PermissionGroup(**get_validate_permission_group(data))
    permission_group.save()
    remove_permissions_cache()
    return PermissionGroupOut.from_orm(permission_group)


@router.get("/api/v1/permission-group/")
def get_permission_group():
    permission_groups = PermissionGroup.objects()
    return {
        "results": [
            PermissionGroupOut.from_orm(permission_group)
            for permission_group in permission_groups
        ]
    }


@router.put("/api/v1/permission-group/{permission_group_id}/")
def update_permission_group(permission_group_id: str, data: PermissionGroupIn):
    PermissionGroup.objects(id=permission_group_id).update_one(
        **get_validate_permission_group(data)
    )
    remove_permissions_cache()
    permission_group = PermissionGroup.objects(id=permission_group_id).first()
    return PermissionGroupOut.from_orm(permission_group)


@router.delete("/api/v1/permission-group/{permission_group_id}/")
def delete_permission_group(permission_group_id: str):
    permission_group = get_object_or_404(PermissionGroup, id=permission_group_id)
    User.objects().update(pull__permissions=permission_group.id)
    permission_group.delete()
    remove_permissions_cache()
    return {"message": "Object deleted"}


@router.post("/api/v1/permission-group/{permission_group_id}/add-users/")
def add_permission_group_users(permission_group_id: str, data: UsersIn):
    permission_group = get_object_or_404(PermissionGroup, id=permission_group_id)
    _ = User.objects(id__in=data.user_ids).update(
        add_to_set__permissions=permission_group.id
    )
    return data


@router.post("/api/v1/permission-group/{permission_group_id}/remove-users/")
def remove_permission_group_users(permission_group_id: str, data: UsersIn):
    permission_group = get_object_or_404(PermissionGroup, id=permission_group_id)
    print(permission_group._data)
    _ = User.objects(id__in=data.user_ids).update(pull__permissions=permission_group.id)
    return {"message": "Users removed"}
