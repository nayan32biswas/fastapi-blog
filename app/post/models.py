from datetime import datetime

from bson.objectid import ObjectId
from mongoengine import (
    BooleanField,
    CASCADE,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    ObjectIdField,
    ReferenceField,
    StringField,
)


class Post(Document):
    user = ReferenceField("User", reverse_delete_rule=CASCADE, required=True)

    name = StringField(max_length=512, required=True)
    content = StringField(required=True)
    image = StringField()

    published_at = DateTimeField()
    is_publish = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class EmbeddedComment(EmbeddedDocument):
    id = ObjectIdField(default=ObjectId, required=True)
    user = ReferenceField("User", required=True)
    content = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Comment(Document):
    user = ReferenceField("User", reverse_delete_rule=CASCADE, required=True)
    post = ReferenceField("Post", reverse_delete_rule=CASCADE, required=True)
    childs = ListField(EmbeddedDocumentField("EmbeddedComment"))

    content = StringField(required=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
