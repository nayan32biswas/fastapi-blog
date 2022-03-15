from datetime import datetime
from typing import Any, List, Optional, Tuple
from bson import ObjectId
from bson.dbref import DBRef

from pydantic import BaseModel, Field
from pymongo import IndexModel, DESCENDING
from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor

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
        if isinstance(v, str):
            return v
        elif isinstance(v, ObjectId):
            return str(v)
        raise TypeError("ObjectId required")


class PydanticObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        elif isinstance(v, str):
            return ObjectId(v)
        raise TypeError("Invalid ObjectId required")


class Document(BaseModel):
    id: PydanticObjectId = Field(default_factory=ObjectId, alias="_id")

    class Config:
        collection_name = None
        allow_inheritance = False
        indexes = []

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
            data = {f"{INHERITANCE_FIELD_NAME}": child, **data}

        inserted_id = db[collection_name].insert_one(data).inserted_id
        if get_obj is True:
            data: Any = db[collection_name].find_one({"_id": inserted_id})
            model = self.__class__
            obj = model(**data)
            self.__dict__.update(obj.dict())
            return obj
        return inserted_id

    def update(self, raw: dict = {}, load_data=False) -> Optional[Any]:
        collection_name, _ = _get_collection_name(self.__class__)
        filter = {"_id": self.id}
        if raw:
            updated_data = raw
        else:
            updated_data = {"$set": self.dict(exclude={"id"})}
        if hasattr(self, "updated_at"):
            datetime_now = datetime.utcnow()
            updated_data["$set"]["updated_at"] = datetime_now
            self.__dict__.update({"updated_at": datetime_now})
        if load_data is True:
            updated = db[collection_name].find_one_and_update(filter, updated_data)
            if updated:
                self.__dict__.update(updated)
                return self
            else:
                return None
        else:
            updated = db[collection_name].update_one(filter, updated_data)
            return updated

    def delete(self) -> Optional[Any]:
        collection_name, _ = _get_collection_name(self.__class__)
        return db[collection_name].delete_one({"_id": self.id})

    @classmethod
    def find(cls, filter: dict = {}, projection: dict = {}) -> Cursor:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        if projection:
            return db[collection_name].find(filter, projection)
        return db[collection_name].find(filter)

    @classmethod
    def raw_or_model(cls, data, raw) -> Optional[Any]:
        if raw:
            return data
        else:
            return cls(**data)

    @classmethod
    def find_first(cls, filter: dict = {}, raw=False) -> Optional[Any]:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        for data in db[collection_name].find(filter).limit(1):
            return cls.raw_or_model(data, raw)
        return None

    @classmethod
    def find_last(cls, filter: dict = {}, raw=False) -> Optional[Any]:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        for data in db[collection_name].find(filter).sort("_id", DESCENDING).limit(1):
            return cls.raw_or_model(data, raw)
        return None

    @classmethod
    def find_one(cls, filter: dict, raw=False) -> Optional[Any]:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        data = db[collection_name].find_one(filter)
        if data:
            return cls.raw_or_model(data, raw)
        else:
            return None

    @classmethod
    def count_documents(cls, filter: dict = {}, **kwargs) -> int:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].count_documents(filter, **kwargs)

    @classmethod
    def exists(cls, filter: dict = {}, **kwargs) -> bool:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].count_documents(filter, **kwargs, limit=1) >= 1

    @classmethod
    def update_one(cls, filter: dict = {}, data: dict = {}, **kwargs) -> int:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        result = db[collection_name].update_one(filter, data, **kwargs)
        return result.matched_count

    @classmethod
    def update_many(cls, filter: dict = {}, data: dict = {}, **kwargs) -> int:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        result = db[collection_name].update_many(filter, data, **kwargs)
        return result.matched_count

    @classmethod
    def aggregate(cls, pipeline: List[Any]) -> CommandCursor:
        collection_name, _ = _get_collection_name(cls)
        return db[collection_name].aggregate(pipeline)

    @property
    def ref(self):
        collection_name, _ = _get_collection_name(self.__class__)
        return PydanticDBRef(collection=collection_name, id=self.id)


def convert_model_to_collection(model: Any) -> str:
    if (
        hasattr(model.Config, "collection_name")
        and model.Config.collection_name is not None
    ):
        """By default model has Config in Basemodel"""
        return model.Config.collection_name
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


class CustomIndexModel(IndexModel):
    _keys = []
    _kwargs = {}

    def __init__(self, keys, **kwargs):
        self._keys = keys
        self._kwargs = kwargs
        super().__init__(keys, **kwargs)

    def __repr__(self) -> str:
        kwargs_str = ", ".join(
            [f"{key}={self._kwargs[key]}" for key in self._kwargs.keys()]
        )
        if len(kwargs_str) > 0:
            kwargs_str = ", " + kwargs_str
        return f"""\n\t\t\tIndexModel({self._keys}{kwargs_str})"""
