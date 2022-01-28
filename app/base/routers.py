from fastapi import APIRouter, Depends, File, status, UploadFile
from app.auth.dependencies import get_authenticated_user

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


@router.post("/upload-image/")
async def create_upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_authenticated_user),
):
    print(user)
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
