import os
import datetime

from fastapi import UploadFile

from app.base.config import BASE_DIR, MEDIA_ROOT
from .string import rand_str


def get_extension(filename):
    name_list = filename.split(".")
    return name_list[-1] if len(name_list) > 1 else ""


def save_image(uploaded_file: UploadFile, folder="image"):
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
