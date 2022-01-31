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


class Comment(EmbeddedDocument):
    id = ObjectIdField(required=True, default=ObjectId)
    childs = EmbeddedDocumentField("Comment")
    user = ReferenceField("User", required=True)

    content = StringField(required=True)

    timestamp = DateTimeField(default=datetime.utcnow)


class Post(Document):
    user = ReferenceField("User", reverse_delete_rule=CASCADE, required=True)

    name = StringField(max_length=512, required=True)
    content = StringField(required=True)
    image = StringField()

    published_at = DateTimeField()
    is_publish = BooleanField(default=True)

    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    comments = ListField(EmbeddedDocumentField(Comment))
