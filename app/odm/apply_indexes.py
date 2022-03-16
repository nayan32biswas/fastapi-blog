from .models import db


def index_for_a_collection(operation):
    """
    First get all incexes for a collection and match with operation.
    Remove full match object.

    If db_index partially match with operation_index then recreate/update it.

    For new_indexes unmatch with db_indexes create new index.
    For db_indexes unmatch with new_indexes drop indexes.
    """
    try:
        collection = db[operation["collection_name"]]
        indexes = operation["create_indexes"]
    except Exception:
        raise Exception("Invalid index object")

    # print(indexes)
    db_indexes = []
    for index in collection.list_indexes():
        temp_val = index.to_dict()
        if "_id" in temp_val["key"]:
            continue
        temp_val.pop("v", None)
        db_indexes.append(temp_val)

    new_indexes = []
    new_indexes_store = {}

    for index in indexes:
        temp_val = index.document
        temp_val["key"] = temp_val["key"].to_dict()
        new_indexes.append(temp_val)
        new_indexes_store[temp_val["name"]] = index

    # print(db_indexes)
    # print(new_indexes)

    update_indexes = []
    for i in range(len(db_indexes)):
        partial_match = None
        for j in range(len(new_indexes)):
            if type(new_indexes[j]) is not dict:
                continue
            if db_indexes[i] == new_indexes[j]:
                db_indexes[i], new_indexes[j] = None, None
                partial_match = None
                break

            """
            # TODO: make a list for partial match
            if pertial match db_indexes[i] with new_indexes[i]:
                parial_match = j
                # not break here check if any other match exist
            """

        if partial_match is not None:
            update_indexes.append((db_indexes[i], new_indexes[partial_match]))
            db_indexes[i], new_indexes[partial_match] = None, None

    delete_db_indexes = [val for val in db_indexes if val]
    new_indexes = [val for val in new_indexes if val]

    # print(delete_db_indexes)
    # print(new_indexes)

    for db_index in delete_db_indexes:
        if db_index is not None:
            collection.drop_index(db_index["name"])
    if len(new_indexes) > 0:
        new_indexes = [
            new_indexes_store[new_index["name"]] for new_index in new_indexes if new_index
        ]
        collection.create_indexes(new_indexes)
    # TODO: apply action for update_indexes

    return len(new_indexes), len(update_indexes), len(delete_db_indexes)


def apply_indexes():
    try:
        from .indexes import operations
    except ImportError:
        raise ImportError(
            """Run "python -m app.main createindexes" before applyindexes"""
        )
    new_index, update_index, delete_index = 0, 0, 0
    for operation in operations:
        ne, up, de = index_for_a_collection(operation)
        new_index += ne
        update_index += up
        delete_index += de
    print()
    if new_index:
        print(new_index, "index created.")
    if update_index:
        print(update_index, "index updated.")
    if delete_index:
        print(delete_index, "index deleted.")
    if [new_index, update_index, delete_index] == [0, 0, 0]:
        print("No change detected.")
    print()


"""
RUN "python -m app.main applyindexes" to apply and indexes create by createindexes inside __init__.py

Import operations from __init__.py inside indexes folter.
Then execute each operations with multiple indexes by a collection.
"""
