from fastapi import APIRouter, Depends


from ..auth.dependencies import get_current_active_user
from .schema import User


router = APIRouter()


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
