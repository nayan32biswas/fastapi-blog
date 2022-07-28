from pymongo import MongoClient

from app.base import config


def get_mongo_client_and_db():
    client = MongoClient(config.DB_URL)
    db = client.get_database()
    return client, db
