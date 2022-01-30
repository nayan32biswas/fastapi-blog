from datetime import datetime

from mongoengine import (
    BooleanField,
    CASCADE,
    DateTimeField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ListField,
    ReferenceField,
    StringField,
)


class Comment(EmbeddedDocument):
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
