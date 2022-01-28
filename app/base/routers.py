from typing import Optional

from fastapi import APIRouter, Cookie, Header, status

from app.user.models import User


router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def home(cookie: Optional[str] = Cookie(None), user_agent: Optional[str] = Header(None)):
    for user in User.objects.all():
        print(user.id)
    return {
        "message": "Hello World",
        "cookie": cookie,
        "User-Agent": user_agent,
    }
