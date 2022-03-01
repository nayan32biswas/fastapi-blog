from typing import Any, List, Optional, Tuple
from bson import ObjectId
from bson.dbref import DBRef

from pydantic import BaseModel, Field

from .utils import camel_to_snake
from app.base import config


mongo_client, db = config.get_mongo_client_and_db()

INHERITANCE_FIELD_NAME = "_cls"


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError("ObjectId required")
        return str(v)


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError("ObjectId required")
        return v


class Document(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        NAME = None

    @classmethod
    def _db(cls) -> str:
        doc_name, _ = _get_collection_name(cls)
        return doc_name

    def __init__(self, *args, **kwargs):
        if type(self) is Document:
            raise Exception(
                "Document is an abstract class and cannot be instantiated directly"
            )
        super().__init__(*args, **kwargs)

    def create(self, get_obj=True) -> Any:
        doc_name, child = _get_collection_name(self.__class__)
        data = self.dict(exclude={"id"})
        if child is not None:
            data[f"{INHERITANCE_FIELD_NAME}"] = child

        inserted_id = db[doc_name].insert_one(data).inserted_id
        if get_obj is True:
            data: Any = db[doc_name].find_one({"_id": inserted_id})
            model = self.__class__
            obj = model(**data)
            self.__dict__.update(obj.dict())
            return obj
        return inserted_id

    def update(self, data):
        doc_name, _ = _get_collection_name(self.__class__)
        updated = db[doc_name].update_one({"_id": self.id}, data)
        return updated

    def delete(self):
        doc_name, _ = _get_collection_name(self.__class__)
        return db[doc_name].delete_one({"_id": self.id})

    @classmethod
    def find(cls, filter: dict = {}):
        doc_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        return db[doc_name].find(filter)

    @classmethod
    def find_one(cls, filter: dict):
        doc_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        data = db[doc_name].find_one(filter)
        if data:
            return cls(**data)

    @classmethod
    def update_one(cls, filter: dict = {}, data: dict = {}, **kwargs):
        doc_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        db[doc_name].update_one(filter, data, **kwargs)
        return True

    @classmethod
    def update_many(cls, filter: dict = {}, data: dict = {}, **kwargs):
        doc_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        return db[doc_name].update_many(filter, data, **kwargs)

    @classmethod
    def aggregate(cls, pipeline: List[Any]):
        doc_name, _ = _get_collection_name(cls)
        return db[doc_name].aggregate(pipeline)

    @property
    def ref(self):
        doc_name, _ = _get_collection_name(self.__class__)
        return PydanticDBRef(collection=doc_name, id=self.id)


def convert_model_to_collection(model: Any) -> str:
    if hasattr(model.Config, "NAME") and model.Config.NAME is not None:
        """By default model has Config in Basemodel"""
        return model.Config.NAME
    else:
        return camel_to_snake(model.__name__)


def _get_collection_name(model: Any) -> Tuple[str, Optional[str]]:
    """
    Return (docname, None).
    Return (parent docname, child docname) if allow_inheritance
    """
    if model.__base__ != Document:
        base_model = model.__base__
        if (
            hasattr(base_model.Config, "allow_inheritance")
            and base_model.Config.allow_inheritance is not True
        ):
            raise Exception(
                f"Invalid model inheritance. {base_model} does not allow model inheritance."
            )
        return convert_model_to_collection(base_model), convert_model_to_collection(model)
    else:
        return convert_model_to_collection(model), None


class PydanticDBRef(DBRef):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, DBRef):
            return v
        if not issubclass(v.__class__, Document) or not hasattr(v, "id"):
            raise TypeError("Invalid Document Model")
        doc_name, _ = _get_collection_name(v.__class__)
        return DBRef(collection=doc_name, id=v.id)
