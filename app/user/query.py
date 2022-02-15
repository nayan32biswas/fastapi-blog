from .models import User


def get_user(
    db,
    or_q: dict = {},
    **kwargs
):
    query = {**kwargs}
    if or_q:
        query['$or'] = []
        for key in or_q.keys():
            query['$or'].append({f'{key}': or_q[key]})
    user = db[User._db].find_one(query)
    if user:
        return User(**user)
    return None
