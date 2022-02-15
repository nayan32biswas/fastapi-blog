from typing import Optional

from pydantic import BaseModel, Field

from app.base.types import ObjectIdStr
from .utils.decorator import staticproperty


class DBBaseModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")

    class Meta:
        DBNAME = None

    @staticproperty
    def _db() -> str:
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        if type(self) is DBBaseModel:
            raise Exception(
                "DBBaseModel is an abstract class and cannot be instantiated directly"
            )
        super().__init__(*args, **kwargs)
