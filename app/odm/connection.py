from pymongo import MongoClient

from app.base import config


_connection = {}


def get_mongo_client_and_db():
    client = MongoClient(config.DB_URL)
    db = client.get_database()
    _connection["db"] = db
    _connection["client"] = client
    return client, db


def _get_connection_client(url: str):
    return MongoClient(url)


def connect(url: str = ""):
    _connection["url"] = url
    _connection["client"] = _get_connection_client(url)


def disconnect():
    _connection["client"].close()


def get_db():
    return _connection["client"].get_database()
