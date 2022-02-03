from datetime import datetime

from mongoengine import (
    BooleanField,
    CASCADE,
    DateTimeField,
    Document,
    ReferenceField,
    StringField,
)


class Content(Document):
    added_by = ReferenceField("User", reverse_delete_rule=CASCADE, required=True)

    name = StringField(max_length=512, required=True)
    image = StringField()

    published_at = DateTimeField()
    is_publish = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {"allow_inheritance": True}


class Course(Content):
    content = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Article(Content):
    content = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
