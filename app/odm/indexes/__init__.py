from pymongo import IndexModel

operations = [
    {
        "collection_name": "user",
        "create_indexes": [
            IndexModel([("username", 1)], unique=True, name="username_1"),
            IndexModel([("email", 1)], unique=True, name="email_1"),
            IndexModel([("last_login", 1)], name="last_login_1"),
            IndexModel(
                [("first_name", 1), ("last_name", 1)],
                unique=True,
                name="first_name_1_last_name_1",
            ),
        ],
    },
    {
        "collection_name": "content",
        "create_indexes": [
            IndexModel([("added_by_id", 1)], name="added_by_id_1"),
            IndexModel([("name", 1)], background=True, sparse=True, name="name_1"),
            IndexModel([("title", 1)], unique=True, name="title_1"),
        ],
    },
]
