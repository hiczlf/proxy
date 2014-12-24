#!/usr/bin/env python
# -*-coding: utf-8 -*-
from time import time
import pickle

class Cache(object):
    def __init__(self, default_timeout=36000, max_cached=300):
        self.default_timeout = default_timeout
        self._cache = {}
        self.clear = self._cache.clear
        self._max_cached = max_cached

    def _prune(self):
        if len(self._cache) > self._max_cached:
            now = time()
            for idx, (key, (expires, _)) in enumerate(self._cache.items()):
                if expires <= now or idx % 3 == 0:
                    self._cache.pop(key, None)

    def get(self, key):
        try:
            expires, value = self._cache[key]
            if expires > time():
                return pickle.loads(value)
        except(KeyError, pickle.PickleError):
            return None

    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout
        self._prune()
        print(key, value)
        self._cache[key] = (time() + timeout, pickle.dumps(value,
            pickle.HIGHEST_PROTOCOL))
        print(self._cache)
        return True
