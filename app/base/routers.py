from fastapi import APIRouter, status

from app.user.models import User


router = APIRouter()


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
def home():
    users = [(user.name, user.username) for user in User.objects.all()]
    return {
        "message": "Hello World",
        "users": users,
    }
