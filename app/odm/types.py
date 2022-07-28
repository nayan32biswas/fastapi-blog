from bson import ObjectId


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

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(format="ObjectId")
        # field_schema.update(type="ObjectId")


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
