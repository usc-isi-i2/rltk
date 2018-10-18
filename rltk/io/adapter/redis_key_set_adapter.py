import redis

from rltk.io.serializer import Serializer, PickleSerializer
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class RedisKeySetAdapter(KeySetAdapter):

    def __init__(self, host, name, key_format='{name}-{key}', serializer: Serializer=None, **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._redis = redis.Redis(host=host, **kwargs)
        self._serializer = serializer
        self._key_format = key_format
        self._name = name
        try:
            self._get_key('test_id')
        except:
            raise ValueError('Invalid key_format.')

    def _get_key(self, key):
        return self._key_format.format(name=self._name, key=key)

    def get(self, key):
        return self._get(self._get_key(key))

    def _get(self, key):
        return set([self._serializer.loads(v) for v in self._redis.smembers(key)])

    def set(self, key, value):
        if not isinstance(value, set):
            raise ValueError('value must be a set')
        self.delete(key)
        for v in value:
            self.add(key, v)

    def add(self, key, value):
        return self._redis.sadd(self._get_key(key), self._serializer.dumps(value))

    def remove(self, key, value):
        return self._redis.srem(self._get_key(key), self._serializer.dumps(value))

    def delete(self, key):
        return self._redis.delete(self._get_key(key))

    def __next__(self):
        # scan_iter() returns generator, keys() returns array
        for key in self._redis.scan_iter(self._get_key('*')):
            yield key.decode('utf-8'), self._get(key)
