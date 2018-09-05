import dbm

from rltk.io.adapter import KeyValueAdapter
from rltk.io.serializer import Serializer, PickleSerializer
from rltk.record import Record


class DBMAdapter(KeyValueAdapter):
    """
    Python builtin `DBM <https://docs.python.org/3.6/library/dbm.html>`_ adapter.
    
    Args:
        filename (str): DBM file name.
        dbm_class (dbm): The value can be `dbm.gnu`, `dbm.ndbm` or `dbm.dumb`.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        
    Note:
        Performance drops when dataset is large.
    """
    def __init__(self, filename, dbm_class=dbm.ndbm, serializer: Serializer = None):
        if not serializer:
            serializer = PickleSerializer()
        self._db = dbm_class.open(filename, 'c')
        self._serializer = serializer

        # not all dbm supports iterator, simulate an iterator by getting a key set
        # key will be in byte form once read out from dbm, needs to be converted to string
        self._ids = set([k.decode('utf-8') for k in self._db.keys()])

    def get(self, record_id):
        return self._serializer.loads(self._db.get(record_id))

    def set(self, record_id, record: Record):
        self._ids.add(record_id)
        self._db[record_id] = self._serializer.dumps(record)

    def __next__(self):
        for i in self._ids:
            yield self.get(i)

    def close(self):
        self._db.close()
