from typing import Optional

from fastapi import APIRouter, Cookie, Header, status

router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def home(cookie: Optional[str] = Cookie(None), user_agent: Optional[str] = Header(None)):
    return {
        "message": "Hello World",
        "cookie": cookie,
        "User-Agent": user_agent,
    }
