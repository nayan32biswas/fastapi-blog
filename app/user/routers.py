from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from mongoengine.queryset.visitor import Q

from app.auth.dependencies import get_authenticated_user
from app.auth.utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
)
from .models import User
from .schemas import UserBase, UserCreate


router = APIRouter(prefix="/api")


@router.get("/v1/me/", response_model=UserBase)
async def get_me(user: User = Depends(get_authenticated_user)):
    return UserBase(**user._data)


@router.post("/v1/registration/", response_model=UserBase)
async def registration(new_user: UserCreate):
    user_exists = User.objects(
        Q(username=new_user.username) | Q(email=new_user.email)
    ).first()
    if user_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User Already Exists",
        )

    user = User(**new_user.dict())
    user.password = get_password_hash(new_user.password)
    user.save()

    return new_user


@router.post("/v1/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Extend or reimplement OAuth2PasswordRequestForm to change authentication format or add additional fields
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"username": user.username})
    refresh_token = create_refresh_token(data={"username": user.username})
    return {
        "token_type": "Bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
