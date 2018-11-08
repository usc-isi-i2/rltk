import dbm

from rltk.io.adapter import KeyValueAdapter
from rltk.io.serializer import Serializer, PickleSerializer


class DbmKeyValueAdapter(KeyValueAdapter):
    """
    Python builtin `DBM <https://docs.python.org/3.6/library/dbm.html>`_ adapter.
    
    Args:
        filename (str): DBM file name.
        dbm_class (dbm): The value can be `dbm.gnu`, `dbm.ndbm` or `dbm.dumb`.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        clean (bool, optional): Clean adapters while starting. Defaults to False.
        
    Note:
        Performance drops when dataset is large.
    """
    def __init__(self, filename, dbm_class=dbm.ndbm, serializer: Serializer = None, clean: bool = False):
        if not serializer:
            serializer = PickleSerializer()
        self._db = dbm_class.open(filename, 'c')
        self._serializer = serializer

        if clean:
            self.clean()

    def get(self, key):
        return self._serializer.loads(self._db.get(key))

    def set(self, key, value):
        self._db[key] = self._serializer.dumps(value)

    def __next__(self):
        for k in self._db.keys():
            key = k.decode('utf-8')
            yield key, self.get(key)

    def delete(self, key):
        del self._db[key]

    def close(self):
        self._db.close()
