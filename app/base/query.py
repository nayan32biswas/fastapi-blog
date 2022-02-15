from bson import ObjectId
from typing import Any, Optional
from fastapi import HTTPException, status

from app.base.models import DBBaseModel

from .types import ObjectIdStr


def get_object_or_404(db: Any, Model: Any, id: Optional[ObjectIdStr] = None, **kwargs) -> DBBaseModel:
    try:
        if id:
            kwargs["_id"] = ObjectId(id)

        obj = db[Model._db].find_one(**kwargs)
        print(obj)
        if obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return obj
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
