from .models import db


def index_for_a_collection(operation):
    """
    First get all incexes for a collection and match with operation.
    Create a list for match_indexes. By default

    If thay are identical then skip it.
    If db_index partially match with operation_index then recreate/update it.

    For operation_indexes unmatch with db_indexes create new index.
    For db_indexes unmatch with operation_indexes drop indexes.
    """
    try:
        collection = db[operation["collection_name"]]
        indexes = operation["create_indexes"]
    except Exception:
        raise Exception("Invalid index object")

    # print(indexes)
    for index in collection.list_indexes():
        print(index)
        print(indexes[0].document)

    print("\n")
    print(dir(indexes[0]))

    for index in indexes:
        print(index.document)

    # new_indexes = indexes
    # collection.create_indexes(new_indexes)


def apply_indexes():
    try:
        from .indexes import operations
    except ImportError:
        raise ImportError(
            """Run "python -m app.main createindexes" before applyindexes"""
        )
    for operation in operations:
        index_for_a_collection(operation)


"""
RUN "python -m app.main applyindexes" to apply and indexes create by createindexes inside __init__.py

Import operations from __init__.py inside indexes folter.
Then execute each operations with multiple indexes by a collection.
"""
