from mongoengine import connect, Document, StringField
from app.base.config import DB_URL

connect(host=DB_URL)


class User(Document):
    name = StringField()
