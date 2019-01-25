import redis

from rltk.record import Record
from rltk.io.adapter import KeyValueAdapter
from rltk.io.serializer import Serializer, PickleSerializer


class RedisKeyValueAdapter(KeyValueAdapter):
    """
    Redis adapter.
    
    Args:
        host (str): Host address.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        key_prefix (str, optional): Prefix of key in redis. Defaults to empty string. 
        clean (bool, optional): Clean adapters while starting. Defaults to False.
        **kwargs: Other parameters used by `redis.Redis <https://redis-py.readthedocs.io/en/latest/#redis.Redis>`_ .
    """
    def __init__(self, host, serializer: Serializer=None, key_prefix: str = '', clean: bool = False, **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._redis = redis.Redis(host=host, **kwargs)
        self._serializer = serializer
        self._key_prefix = key_prefix

        if clean:
            self.clean()

    #: parallel-safe
    parallel_safe = True

    def _encode_key(self, key):
        return self._key_prefix + key

    def _decode_key(self, key):
        key = key.decode('utf-8')
        return key[len(self._key_prefix):]

    def get(self, key) -> object:
        v = self._redis.get(self._encode_key(key))
        if v:
            return self._serializer.loads(v)

    def set(self, key, value: object):
        return self._redis.set(self._encode_key(key), self._serializer.dumps(value))

    def delete(self, key):
        return self._redis.delete(self._encode_key(key))

    def __next__(self):
        # scan_iter() returns generator, keys() returns array
        for key in self._redis.scan_iter(self._encode_key('*')):
            yield self._decode_key(key), self._serializer.loads(self._redis.get(key))
