from typing import Any, Optional
from bson import ObjectId

from pydantic import BaseModel, Field

from app.base.types import ObjectIdStr
from app.base.utils.string import camel_to_snake
from .utils.decorator import staticproperty


def get_doc_name(model: Any) -> str:
    if hasattr(model, "Meta") and hasattr(model.Meta, "NAME"):
        return model.Meta.NAME
    else:
        return camel_to_snake(model.__name__)


class DBBaseModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(default=None, alias="_id")

    class Meta:
        NAME = None

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
        doc_name = get_doc_name(self.__class__)
        inserted_id = db[doc_name].insert_one(self.dict()).inserted_id
        if get_obj is True:
            obj: Any = db[doc_name].find_one({"_id": inserted_id})
            model = self.__class__
            return model(**obj)
        return inserted_id

    def update(self, db: Any, **kwargs):
        doc_name = get_doc_name(self.__class__)
        updated = db[doc_name].delete_one({"_id": ObjectId(self.id)}, {"$set": kwargs})
        return updated

    def delete(self, db: Any):
        doc_name = get_doc_name(self.__class__)
        return db[doc_name].delete_one({"_id": ObjectId(self.id)})

    @classmethod
    def find(cls, db: Any, filter: dict = {}):
        doc_name = get_doc_name(cls)
        return db[doc_name].find(filter)

    @classmethod
    def find_one(cls, db: Any, filter: dict = {}):
        doc_name = get_doc_name(cls)
        return db[doc_name].find_one(filter)

    @classmethod
    def update_many(cls, db: Any, filter: dict, data: dict, **kwargs):
        doc_name = get_doc_name(cls)
        return db[doc_name].update_many(filter, data, **kwargs)
