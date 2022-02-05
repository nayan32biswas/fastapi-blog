from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.base.utils import get_object_or_404
from app.user.models import User

from .schemas import (
    PermissionGroupAddUserIn,
    PermissionGroupUpdate,
    Token,
    PermissionGroupIn,
    PermissionGroupOut,
)
from .utils import authenticate_user, create_access_token
from .models import Permission, PermissionGroup

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


@router.post("/api/v1/permission-group/")
def create_permission_group(data: PermissionGroupIn):
    permissions = []
    for permission in data.permissions:
        value = "".join(sorted(set(permission.value)))
        permissions.append(Permission(type=permission.type, value=value))
    permission_group = PermissionGroup(
        name=data.name, description=data.description, permissions=permissions
    )
    permission_group.save()
    return PermissionGroupOut.from_orm(permission_group)


@router.get("/api/v1/permission-group/")
def get_permission_group(data: PermissionGroupIn):
    permission_groups = PermissionGroup.objects()
    return {
        "results": [
            PermissionGroupOut.from_orm(permission_group)
            for permission_group in permission_groups
        ]
    }


@router.put("/api/v1/permission-group/{permission_group_id}/")
def update_permission_group(permission_group_id: str, data: PermissionGroupUpdate):
    PermissionGroup.objects(id=permission_group_id).update_one(
        name=data.name, description=data.description
    )
    permission_group = PermissionGroup.objects(id=permission_group_id).first()
    return PermissionGroupUpdate.from_orm(permission_group)


@router.post("/api/v1/permission-group/{permission_group_id}/add-users/")
def add_permission_group_users(permission_group_id: str, data: PermissionGroupAddUserIn):
    permission_group = get_object_or_404(PermissionGroup, id=permission_group_id)

    users = User.objects(id__in=data.user_ids).update(
        add_to_set__permissions=permission_group.id
    )
    print(users)

    # permission_group.update(push__permissions=embedded_permission_group)
    # print(updated)
    return data
