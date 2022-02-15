from typing import Any, Optional
from bson import ObjectId

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

    def create(self, db: Any, get_obj=True) -> BaseModel:
        model = self.__class__
        inserted_id = db[model._db].insert_one(self.dict()).inserted_id
        if get_obj is True:
            obj: Any = db[model._db].find_one({"_id": inserted_id})
            return model(**obj)
        return inserted_id

    def update(self, db: Any, **kwargs):
        model = self.__class__
        updated = db[model._db].delete_one({"_id": ObjectId(self.id)}, {"$set": kwargs})
        return updated

    def delete(self, db: Any):
        model = self.__class__
        return db[model._db].delete_one({"_id": ObjectId(self.id)})
