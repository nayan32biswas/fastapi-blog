from bson import ObjectId
from typing import Any, Optional
from fastapi import HTTPException, status

from app.base.models import Document


def get_object_or_404(
    db: Any, Model: Any, id: Optional[str] = None, **kwargs
) -> Document:
    if id:
        kwargs["_id"] = ObjectId(id)
    obj = Model.find_one(db, kwargs)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return obj
