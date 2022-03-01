from typing import Any, List, Optional, Tuple
from bson import ObjectId
from bson.dbref import DBRef

from pydantic import BaseModel, Field

from .utils import camel_to_snake
from .connection import get_mongo_client_and_db

mongo_client, db = get_mongo_client_and_db()

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
        collection_name, _ = _get_collection_name(cls)
        return collection_name

    def __init__(self, *args, **kwargs):
        if type(self) is Document:
            raise Exception(
                "Document is an abstract class and cannot be instantiated directly"
            )
        super().__init__(*args, **kwargs)

    def create(self, get_obj=True) -> Any:
        collection_name, child = _get_collection_name(self.__class__)
        data = self.dict(exclude={"id"})
        if child is not None:
            data[f"{INHERITANCE_FIELD_NAME}"] = child

        inserted_id = db[collection_name].insert_one(data).inserted_id
        if get_obj is True:
            data: Any = db[collection_name].find_one({"_id": inserted_id})
            model = self.__class__
            obj = model(**data)
            self.__dict__.update(obj.dict())
            return obj
        return inserted_id

    def update(self, data):
        collection_name, _ = _get_collection_name(self.__class__)
        updated = db[collection_name].update_one({"_id": self.id}, data)
        return updated

    def delete(self):
        collection_name, _ = _get_collection_name(self.__class__)
        return db[collection_name].delete_one({"_id": self.id})

    @classmethod
    def find(cls, filter: dict = {}):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        return db[collection_name].find(filter)

    @classmethod
    def find_one(cls, filter: dict):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        data = db[collection_name].find_one(filter)
        if data:
            return cls(**data)

    @classmethod
    def update_one(cls, filter: dict = {}, data: dict = {}, **kwargs):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        db[collection_name].update_one(filter, data, **kwargs)
        return True

    @classmethod
    def update_many(cls, filter: dict = {}, data: dict = {}, **kwargs):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter[f"{INHERITANCE_FIELD_NAME}"] = child
        return db[collection_name].update_many(filter, data, **kwargs)

    @classmethod
    def aggregate(cls, pipeline: List[Any]):
        collection_name, _ = _get_collection_name(cls)
        return db[collection_name].aggregate(pipeline)

    @property
    def ref(self):
        collection_name, _ = _get_collection_name(self.__class__)
        return PydanticDBRef(collection=collection_name, id=self.id)


def convert_model_to_collection(model: Any) -> str:
    if hasattr(model.Config, "NAME") and model.Config.NAME is not None:
        """By default model has Config in Basemodel"""
        return model.Config.NAME
    else:
        return camel_to_snake(model.__name__)


def _get_collection_name(model: Any) -> Tuple[str, Optional[str]]:
    """
    Return (collectionname, None).
    Return (parent collectionname, child collectionname) if allow_inheritance
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
        collection_name, _ = _get_collection_name(v.__class__)
        return DBRef(collection=collection_name, id=v.id)
