import os
from pathlib import Path
from typing import List

from .models import Document, _get_collection_name


MIGRATIONS_PATH = "migrations"
starint_of_migration_file = """from pymongo import IndexModel"""


def get_migration_path():
    path = Path(__file__).resolve().parent
    migrations_path = os.path.join(path, MIGRATIONS_PATH)
    if os.path.exists(migrations_path) is False:
        os.mkdir(migrations_path)
    return migrations_path


def object_parser(operation):
    return "\t" + str(
        {
            "collection_name": operation["collection_name"],
            "create_indexes": [idx for idx in operation["create_indexes"]],
        }
    )


def write_migration_file(operations):
    migrations_path = get_migration_path()
    init_file_path = os.path.join(migrations_path, "__init__.py")
    data = ",\n".join([object_parser(operation) for operation in operations])
    final_string = f"""{starint_of_migration_file}\n\n\noperations = [\n{data}\n]\n"""
    with open(init_file_path, "wb") as temp_file:
        temp_file.write(final_string.encode())


def get_indexes(model) -> List:
    if hasattr(model.Config, "indexes"):
        return list(model.Config.indexes)
    return []


def create_migrations():
    operations = []
    for model in Document.__subclasses__():
        indexes = get_indexes(model)
        if indexes:
            collection_name, _ = _get_collection_name(model)
            obj = {"collection_name": collection_name, "create_indexes": indexes}
            if (
                hasattr(model.Config, "allow_inheritance")
                and model.Config.allow_inheritance is True
            ):
                """If a model has child model"""
                for child_model in model.__subclasses__():
                    indexes += get_indexes(child_model)
            operations.append(obj)
            # TODO: match with existing index and drop_index if remove from model
    write_migration_file(operations)
