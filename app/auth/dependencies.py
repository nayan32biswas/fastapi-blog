import jwt
from typing import Any

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordBearer

from app.auth.models import get_cached_or_db_permissions
from app.auth.permission import PermissionType, PermissionValueChar, UserRoles
from app.base.config import (
    SECRET_KEY,
    ALGORITHM,
)
from app.user.models import User
from app.user.query import get_user
from .schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_authenticated_token(token: str = Depends(oauth2_scheme)):
    try:
        payload: Any = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    return token_data


async def get_authenticated_user(
    token_data: TokenData = Depends(get_authenticated_token)
):
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_admin_user(
    token_data: TokenData = Depends(get_authenticated_token)
):
    # user = User.objects(username=token_data.username, role=UserRoles.ADMIN).first()
    user = get_user(username=token_data.username, role=UserRoles.ADMIN)
    if user is None:
        raise credentials_exception
    if user.is_active is False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def has_post_delete_permission(user: User):
    permissions = get_cached_or_db_permissions(
        user_perm_group_ids=user.permissions, permission_type=PermissionType.POST
    )
    for permission in permissions:
        if PermissionValueChar.DELETE.value in permission["value"]:
            return True
    return False
