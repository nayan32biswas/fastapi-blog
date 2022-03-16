import os
import subprocess
from pathlib import Path
from typing import List

from .models import Document, _get_collection_name


INDEXES_PATH = "indexes"
starint_of_indexes_file = """from pymongo import IndexModel\n\n"""


def get_indexes_path():
    path = Path(__file__).resolve().parent
    indexes_path = os.path.join(path, INDEXES_PATH)
    if os.path.exists(indexes_path) is False:
        os.mkdir(indexes_path)
    return indexes_path


def object_parser(operation):
    # return json.dumps(operation, indent=4, default=str)
    return str(
        {
            "collection_name": operation["collection_name"],
            "create_indexes": [idx for idx in operation["create_indexes"]],
        }
    )


def write_indexes_file(operations):
    indexes_path = get_indexes_path()
    init_file_path = os.path.join(indexes_path, "__init__.py")
    data = ",".join([object_parser(operation) for operation in operations])
    final_string = f"""{starint_of_indexes_file}operations = [{data}]"""
    with open(init_file_path, "wb") as temp_file:
        temp_file.write(final_string.encode())
    # Format the indexes file code
    subprocess.run(["black", f"app/odm/{INDEXES_PATH}/"])


def get_indexes(model) -> List:
    if hasattr(model.Config, "indexes"):
        return list(model.Config.indexes)
    return []


def create_indexes():
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
    write_indexes_file(operations)


"""
"python -m app.main createindexes" will create __init__.py inside indexess folder inside of odm module.

The way of create_indexess works first it imports all child models of Document since it's the abstract parent model.
Then retrieve all the child modules and will try to get indexes inside the Config class.
All indexes objects should be inserted as it is into operations of __init__.py file.
And format it with a "black" code formater.

If some collection was deleted and indexes exists just don't do anything it will handle by DB admin.
"""
