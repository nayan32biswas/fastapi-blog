from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from app.auth.dependencies import get_authenticated_user
from app.auth.firebase_auth import decode_firetoken
from app.auth.utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    create_refresh_token,
)
from app.user.query import get_user
from .models import User
from .schemas import UserBase, UserCreate


router = APIRouter(prefix="/api")


@router.get("/v1/me/", response_model=UserBase)
async def get_me(user: User = Depends(get_authenticated_user)):
    return user


@router.post("/v1/registration/")
async def registration(new_user: UserCreate):
    # user = User.objects(
    #     Q(username=new_user.username) | Q(email=new_user.email)
    # ).first()
    user = get_user(or_q={"username": new_user.username, "email": new_user.email})
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User Already Exists",
        )
    user = User(**new_user.dict())
    user.password = get_password_hash(user.password)
    user.create()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=UserBase.from_orm(new_user).dict()
    )


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


@router.post("/v1/firebase/")
async def firebase(
    fire_token: str = Form(...),
):
    fire_payload = decode_firetoken(fire_token)
    if fire_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"uid": fire_payload.get("uid")})
    refresh_token = create_refresh_token(data={"uid": fire_payload.get("uid")})
    return {
        "token_type": "Bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
