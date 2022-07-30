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
    if "client" in _connection:
        return _connection["client"]
    _connection["url"] = url
    _connection["client"] = _get_connection_client(url)


def disconnect():
    _connection["client"].close()
    del _connection["client"]


def get_db():
    if not _connection or "client" not in _connection:
        if "url" in _connection:
            connect(_connection["url"])
        else:
            raise Exception("DB connection is not provided")
    return _connection["client"].get_database()
