from bson import ObjectId
from typing import Any, Optional
from fastapi import HTTPException, status

from app.base.models import Document

from .types import ObjectIdStr


def get_object_or_404(
    db: Any, Model: Any, id: Optional[ObjectIdStr] = None, **kwargs
) -> Document:
    try:
        if id:
            kwargs["_id"] = ObjectId(id)
        obj = Model.find_one(db, **kwargs)
        if obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return obj
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
