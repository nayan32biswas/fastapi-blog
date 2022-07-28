from bson import ObjectId
from typing import Any, Optional, Union
from fastapi import HTTPException, status

from app.odm.types import ObjectIdStr


def get_object_or_404(Model: Any, id: Optional[Union[str, ObjectIdStr]] = None, **kwargs):
    if id is not None:
        kwargs["_id"] = id if type(id) == ObjectId else ObjectId(id)
    obj = Model.find_one(kwargs)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return obj
