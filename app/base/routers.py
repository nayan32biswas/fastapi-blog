import os

from fastapi import APIRouter, Depends, File, HTTPException, status, Request, UploadFile
from fastapi.responses import FileResponse
from app.auth.dependencies import get_authenticated_token
from app.base.config import MEDIA_ROOT
from app.base.utils.file import save_image

from app.user.models import User
from . import ws_router


router = APIRouter()

router.include_router(ws_router.router)


@router.get("/", status_code=status.HTTP_200_OK)
def home():
    return {"message": "Hello World"}


@router.post("/upload-image/")
async def create_upload_image(
    image: UploadFile = File(...),
    _: User = Depends(get_authenticated_token),
):
    image_path = save_image(image, folder="image")
    return image_path


# @router.get("/media/{folder}/{date}/{imagename}")
# async def get_image(folder: str, date: str, imagename: str):
#     return FileResponse(f"{MEDIA_ROOT}/{folder}/{date}/{imagename}")


@router.get("/media/{file_path:path}")
async def get_image(request: Request, file_path: str):
    file_path = f"{MEDIA_ROOT}/{file_path}"

    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
