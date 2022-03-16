from pymongo import IndexModel

operations = [
    {
        "collection_name": "user",
        "create_indexes": [
            IndexModel([("username", 1)], unique=True),
            IndexModel([("email", 1)], unique=True),
            IndexModel([("first_name", 1), ("last_name", 1)], unique=True),
        ],
    },
    {
        "collection_name": "content",
        "create_indexes": [
            IndexModel([("added_by_id", 1)]),
            IndexModel([("name", 1)], background=True, sparse=True),
            IndexModel([("title", 1)], unique=True),
        ],
    },
]
