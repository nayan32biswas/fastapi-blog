from typing import Any, List
from bson import ObjectId

from pydantic import BaseModel, Field

from app.base.types import PydanticObjectId
from app.base.utils.string import camel_to_snake
from .utils.decorator import staticproperty


def _get_doc_name(model: Any) -> str:
    if hasattr(model.Config, "NAME") and model.Config.NAME is not None:
        return model.Config.NAME
    else:
        return camel_to_snake(model.__name__)


class Document(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        NAME = None

    @staticproperty
    def _db() -> str:
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        if type(self) is Document:
            raise Exception(
                "Document is an abstract class and cannot be instantiated directly"
            )
        super().__init__(*args, **kwargs)

    def create(self, db: Any, get_obj=True) -> Any:
        doc_name = _get_doc_name(self.__class__)
        inserted_id = db[doc_name].insert_one(self.dict(exclude={"id"})).inserted_id
        if get_obj is True:
            obj: Any = db[doc_name].find_one({"_id": inserted_id})
            model = self.__class__
            return model(**obj)
        return inserted_id

    def update(self, db: Any, data):
        doc_name = _get_doc_name(self.__class__)
        updated = db[doc_name].update_one({"_id": self.id}, data)
        return updated

    def delete(self, db: Any):
        doc_name = _get_doc_name(self.__class__)
        return db[doc_name].delete_one({"_id": self.id})

    @classmethod
    def find(cls, db: Any, filter: dict):
        doc_name = _get_doc_name(cls)
        return db[doc_name].find(filter)

    @classmethod
    def find_one(cls, db: Any, filter: dict):
        doc_name = _get_doc_name(cls)
        data = db[doc_name].find_one(filter)
        if data:
            return cls(**data)

    @classmethod
    def update_one(cls, db: Any, filter: dict, data: dict, **kwargs):
        doc_name = _get_doc_name(cls)
        data = db[doc_name].update_one(filter, data, **kwargs)
        return True

    @classmethod
    def update_many(cls, db: Any, filter: dict, data: dict, **kwargs):
        doc_name = _get_doc_name(cls)
        return db[doc_name].update_many(filter, data, **kwargs)

    @classmethod
    def aggregate(cls, db: Any, pipeline: List[Any]):
        doc_name = _get_doc_name(cls)
        return db[doc_name].aggregate(pipeline)
