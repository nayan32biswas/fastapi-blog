from mongoengine import Document
from fastapi import HTTPException, status


def get_object_or_404(Model: Document, **kwargs):
    try:
        return Model.objects.get(**kwargs)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
