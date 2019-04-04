import os

from rltk.io.serializer import Serializer, PickleSerializer
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.utils import module_importer


plyvel = module_importer('plyvel', 'plyvel>=1.0.5', '''
If you are using Mac and installed LevelDB by HomeBrew, 
please make sure that `plyvel` refers to correct library file while installing:

    pip uninstall plyvel
    CFLAGS='-mmacosx-version-min=10.7 -stdlib=libc++' pip install --no-cache-dir plyvel
''')


class LevelDbKeySetAdapter(KeySetAdapter):
    """
    `LevelDB <https://github.com/google/leveldb>`_ key set adapter. 
    LevelDB is a serverless, stand-alone key value store. It can be used as a local file system store.
    
    
    Args:
        path (str): The directory path used by LevelDB.
        name (str): Because LevelDB only has a single key space, \
                    this is used as name space.
        serializer (Serializer, optional): The serializer used to serialize each object in set. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        clean (bool, optional): Clean adapters while starting. Defaults to False.
        kwargs: Other key word arguments for `plyvel.DB <https://plyvel.readthedocs.io/en/latest/api.html#DB>`_.
        
    Note:
        A particular LevelDB database only supports accessing by one process at one time. 
        This adapter uses singleton (in one RLTK instance) to make sure only one `plyvel.DB` is created.
        Different `name` s can be used if you don't want to create multiple databases.
    """
    _db_instance = None
    _db_ref_count = 0

    def __init__(self, path: str, name: str, serializer: Serializer = None, clean: bool = False, **kwargs):
        if not serializer:
            serializer = PickleSerializer()

        # leveldb's connection can only be a singleton
        if not self.__class__._db_instance:
            if not os.path.exists(path):
                os.mkdir(path)
            self.__class__._db_instance = plyvel().DB(path, create_if_missing=True, **kwargs)
        self._db = self.__class__._db_instance
        self.__class__._db_ref_count += 1

        self._prefix = '{name}_'.format(name=name)
        self._prefix_db = self._db.prefixed_db(self._encode(self._prefix))
        self._serializer = serializer

        if clean:
            self.clean()

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
