from datetime import datetime
from typing import Any, List, Optional, Tuple
from typing_extensions import Self
from bson import ObjectId

from pydantic import BaseModel, Field
from pymongo import DESCENDING
from pymongo.cursor import Cursor


from app.odm.fields import PydanticDBRef as _PydanticDBRef
from app.odm.types import PydanticObjectId as _PydanticObjectId
from .utils import camel_to_snake
from .connection import get_mongo_client_and_db

mongo_client, db = get_mongo_client_and_db()

INHERITANCE_FIELD_NAME = "_cls"


class Document(BaseModel):
    id: _PydanticObjectId = Field(default_factory=ObjectId, alias="_id")
    v2_id: Optional[int] = None

    class Config:
        # Those fields will work as the default value of any child class.
        orm_mode = True
        allow_population_by_field_name = True
        collection_name = None
        allow_inheritance = False

    @classmethod
    def _db(cls) -> str:
        collection_name, _ = _get_collection_name(cls)
        return collection_name

    @property
    def ref(self):
        collection_name, _ = _get_collection_name(self.__class__)
        return _PydanticDBRef(collection=collection_name, id=self.id)

    def __init__(self, *args, **kwargs):
        if type(self) is Document:
            raise Exception(
                "Document is an abstract class and cannot be instantiated directly"
            )
        super().__init__(*args, **kwargs)

    def create(self, get_obj=False) -> Self:
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
        else:
            self.__dict__.update({"id": inserted_id})
            return self

    @classmethod
    def get_or_create(cls, **kwargs) -> Tuple[Self, bool]:
        obj = cls.find_last(kwargs)
        if obj:
            return obj, False
        return cls(**kwargs).create(), True

    @classmethod
    def find_raw(cls, filter: dict = {}, projection: dict = {}) -> Cursor:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        if projection:
            return db[collection_name].find(filter, projection)
        return db[collection_name].find(filter)

    @classmethod
    def find(
        cls,
        filter: dict = {},
        sort: Optional[List[Tuple[str, int]]] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        qs = cls.find_raw(filter)
        if sort:
            qs = qs.sort(sort)
        if skip:
            qs = qs.skip(skip)
        if limit:
            qs = qs.limit(limit)

        model_childs = {}
        is_dynamic_model = False
        if (
            hasattr(cls.Config, "allow_inheritance")
            and cls.Config.allow_inheritance is True
        ):
            is_dynamic_model = True
            for model in cls.__subclasses__():
                _, child = _get_collection_name(model)
                model_childs[child] = model

        for data in qs:
            if is_dynamic_model and data[INHERITANCE_FIELD_NAME] in model_childs:
                yield model_childs[data[INHERITANCE_FIELD_NAME]](**data)
            else:
                yield cls(**data)

    @classmethod
    def find_one(
        cls, filter: dict = {}, sort: Optional[List[Tuple[str, int]]] = None
    ) -> Optional[Self]:
        qs = cls.find_raw(filter)
        if sort:
            qs = qs.sort(sort)
        for data in qs.limit(1):
            """limit 1 is equivalent to find_one and that is implemented in pymongo find_one"""
            return cls(**data)
        return None

    @classmethod
    def find_first(
        cls, filter: dict = {}, sort: Optional[List[Tuple[str, int]]] = None
    ) -> Optional[Self]:
        return cls.find_one(filter, sort=sort)

    @classmethod
    def find_last(
        cls,
        filter: dict = {},
        sort: Optional[List[Tuple[str, int]]] = [("_id", DESCENDING)],
    ) -> Optional[Self]:
        return cls.find_one(filter, sort=sort)

    @classmethod
    def count_documents(cls, filter: dict = {}, **kwargs) -> int:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].count_documents(filter, **kwargs)

    @classmethod
    def exists(cls, filter: dict = {}, **kwargs) -> Any:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].count_documents(filter, **kwargs, limit=1) >= 1

    @classmethod
    def aggregate(cls, pipeline: List[Any]):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            pipeline = [{"$match": {f"{INHERITANCE_FIELD_NAME}": child}}] + pipeline
        return db[collection_name].aggregate(pipeline)

    @classmethod
    def get_random_one(cls, filter: dict = {}):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter[INHERITANCE_FIELD_NAME] = child
        pipeline = [{"$match": filter}, {"$sample": {"size": 1}}]
        for each in db[collection_name].aggregate(pipeline):
            return each
        return None

    def update(self, raw: dict = {}):
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

        return db[collection_name].update_one(filter, updated_data)

    @classmethod
    def update_one(cls, filter: dict = {}, data: dict = {}, **kwargs) -> Any:
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].update_one(filter, data, **kwargs)

    @classmethod
    def update_many(cls, filter: dict = {}, data: dict = {}, **kwargs):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].update_many(filter, data, **kwargs)

    def delete(self):
        collection_name, _ = _get_collection_name(self.__class__)
        return db[collection_name].delete_one({"_id": self.id})

    @classmethod
    def delete_many(cls, filter: dict = {}):
        collection_name, child = _get_collection_name(cls)
        if child is not None:
            filter = {f"{INHERITANCE_FIELD_NAME}": child, **filter}
        return db[collection_name].delete_many(filter)


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


__all__ = ["INHERITANCE_FIELD_NAME", "Document"]
