import os
import plyvel

from rltk.io.serializer import Serializer, PickleSerializer
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class LevelDbKeySetAdapter(KeySetAdapter):
    """
    https://plyvel.readthedocs.io/en/latest/api.html#DB
    """
    _db_instance = None
    _db_ref_count = 0

    def __init__(self, path, name, serializer: Serializer=None):
        if not serializer:
            serializer = PickleSerializer()

        # leveldb's connection can only be a singleton
        if not self.__class__._db_instance:
            if not os.path.exists(path):
                os.mkdir(path)
            self.__class__._db_instance = plyvel.DB(path, create_if_missing=True)
        self._db = self.__class__._db_instance
        self.__class__._db_ref_count += 1

        self._prefix = '{name}_'.format(name=name)
        self._prefix_db = self._db.prefixed_db(self._encode(self._prefix))
        self._serializer = serializer

    @staticmethod
    def _encode(string):
        return string.encode(encoding='utf-8')

    @staticmethod
    def _decode(bytes_):
        return bytes_.decode(encoding='utf-8')

    def _get(self, key):
        v = self._prefix_db.get(key)
        if not v:
            return
        return self._serializer.loads(v)

    def get(self, key):
        return self._get(self._encode(key))

    def set(self, key, value):
        if not isinstance(value, set):
            raise ValueError('value must be a set')
        self.delete(key)
        self._prefix_db.put(self._encode(key), self._serializer.dumps(value))

    def add(self, key, value):
        set_ = self.get(key)
        if not set_:
            set_ = set([])
        set_.add(value)
        return self.set(key, set_)

    def remove(self, key, value):
        set_ = self.get(key)
        if not set_:
            return
        set_.remove(value)
        return self.set(key, set_)

    def delete(self, key):
        return self._prefix_db.delete(self._encode(key))

    def __next__(self):
        for key in self._prefix_db.iterator(include_value=False):
            yield self._decode(key), self._get(key)

    def close(self):
        self.__class__._db_ref_count -= 1
        if self.__class__._db_ref_count == 0:
            self._db.close()
