import json

import redis

from .config import REDIS_CONNECTION_CONFIG


class RedisHelper:
    def __init__(self, key=None, data=None):
        self.data = data
        self.key = key
        self.redis = self.get_conn()

    def get_conn():
        try:
            r = redis.Redis(**REDIS_CONNECTION_CONFIG, decode_responses=True)
            return r
        except Exception:
            return None

    def get_data(self):
        if self.redis:
            try:
                data = self.redis.get(self.key)
                if data:
                    return json.loads(data)
            except Exception:
                return None
        else:
            return None

    def set_data(self, time=6000):
        if self.redis and self.data:
            try:
                self.redis.setex(name=self.key, time=time, value=json.dumps(self.data))
                return True
            except Exception:
                return False
        else:
            return False

    def delete_data(self):
        if self.redis and self.key:
            for key in self.redis.keys(self.key):
                self.redis.delete(key)
