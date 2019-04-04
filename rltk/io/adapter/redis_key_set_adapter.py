import redis

from rltk.io.serializer import Serializer, PickleSerializer
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.utils import module_importer


redis = module_importer('redis', 'redis>=2.0.0')


class RedisKeySetAdapter(KeySetAdapter):
    """
    Redis key set adapter.
    
    Args:
        host (str): Host address.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        key_prefix (str, optional): Prefix of key in redis. Defaults to empty string.
        clean (bool, optional): Clean adapters while starting. Defaults to False.
        **kwargs: Other parameters used by `redis.Redis <https://redis-py.readthedocs.io/en/latest/#redis.Redis>`_ .
    """

    def __init__(self, host, key_prefix: str = '', serializer: Serializer=None, clean: bool = False, **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._redis = redis().Redis(host=host, **kwargs)
        self._serializer = serializer
        self._key_prefix = key_prefix

        if clean:
            self.clean()

    def _encode_key(self, key):
        return '{prefix}{key}'.format(prefix=self._key_prefix, key=key)

    def _decode_key(self, key):
        key = key.decode('utf-8')
        return key[len(self._key_prefix):]

    def get(self, key):
        return self._get(self._encode_key(key))

    def _get(self, key):
        v = set([self._serializer.loads(v) for v in self._redis.smembers(key)])
        if len(v) != 0:
            return v

    def set(self, key, value):
        if not isinstance(value, set):
            raise ValueError('value must be a set')
        self.delete(key)
        for v in value:
            self.add(key, v)

    def add(self, key, value):
        return self._redis.sadd(self._encode_key(key), self._serializer.dumps(value))

    def remove(self, key, value):
        return self._redis.srem(self._encode_key(key), self._serializer.dumps(value))

    def delete(self, key):
        return self._redis.delete(self._encode_key(key))

    def __next__(self):
        # scan_iter() returns generator, keys() returns array
        for key in self._redis.scan_iter(self._encode_key('*')):
            yield self._decode_key(key), self._get(key)
