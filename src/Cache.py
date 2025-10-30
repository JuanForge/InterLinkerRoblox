import threading
class Cache:
    def __init__(self, cache: dict, Lock: threading.Lock):
        self.cache = cache
        self.lock = Lock

    def get(self, path):
        with self.lock:
            return self.cache.get(path, None)

    def set(self, path, value):
        with self.lock:
            self.cache[path] = value

session = Cache({"type:1": {}, "TotalTime": 0.0}, threading.Lock())
session.set(["type:1"]["5074904065"], {"id": ["5074904065"]})