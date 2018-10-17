import dbm

from rltk.io.adapter import DatasetAdapter
from rltk.io.serializer import Serializer, PickleSerializer
from rltk.record import Record


class DbmDatasetAdapter(DatasetAdapter):
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

    def get(self, record_id):
        return self._serializer.loads(self._db.get(record_id))

    def set(self, record_id, record: Record):
        self._db[record_id] = self._serializer.dumps(record)

    def __next__(self):
        for k in self._db.keys():
            id_ = k.decode('utf-8')
            yield self.get(id_)

    def close(self):
        self._db.close()
