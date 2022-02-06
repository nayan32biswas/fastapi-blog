import json

import redis

from .config import REDIS_CONNECTION_CONFIG


class RedisHelper:
    def __init__(self, key=None, data=None):
        self.data = data
        self.key = key
        self.redis = self.get_conn()

    def get_conn(self):
        try:
            r = redis.StrictRedis(**REDIS_CONNECTION_CONFIG, decode_responses=True)
            print(r)
            return r
        except Exception:
            return None

    def get_data(self):
        print("start")
        if self.redis:
            print("TRYING")
            try:
                print("\n\ndata")
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

    def get_data_list(self, keys=[]):
        if self.redis:
            try:
                data_list = self.redis.mget(keys)
                if data_list:
                    return [json.loads(data) for data in data_list if data]
            except Exception:
                return None
        else:
            return None

    def delete_data(self):
        if self.redis and self.key:
            for key in self.redis.keys(self.key):
                self.redis.delete(key)


"""
import os, redis, json
r = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)

r.setex(name="one", time=600, value=json.dumps({"key": "data one"}))
r.setex(name="two", time=600, value=json.dumps({"key": "data two"}))
r.setex(name="three", time=600, value=json.dumps({"key": "data three"}))
r.setex(name="four", time=600, value=json.dumps({"key": "data four"}))

r.get("one")

keys = ["one", "three"]

[json.loads(data) for data in r.mget(keys) if data]
"""
