import os
import datetime
from random import choice
from string import ascii_lowercase, digits

from mongoengine import Document
from fastapi import File, HTTPException, status

from app.base.config import BASE_DIR, MEDIA_ROOT


def rand_str(N=12):
    return "".join(choice(ascii_lowercase + digits) for _ in range(N))


def get_extension(filename):
    name_list = filename.split(".")
    return name_list[-1] if len(name_list) > 1 else ""


def save_image(uploaded_file: File, folder="image"):
    if not uploaded_file:
        return ""
    extension = get_extension(uploaded_file.filename)
    now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    folder_location = f"{MEDIA_ROOT}/{folder}/{now[:6]}/{rand_str(4)}{now}"

    if not os.path.exists(folder_location):
        os.makedirs(folder_location)

    file_location = f"{folder_location}.{extension}"
    while os.path.isfile(file_location):
        folder_location += rand_str(4)
        file_location = f"{folder_location}.{extension}"
    try:
        with open(file_location, "wb+") as file_object:
            file_object.write(uploaded_file.file.read())
        return file_location.split(f"{BASE_DIR}")[-1]
    except Exception:
        return ""


def get_object_or_404(Model: Document, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
