import dbm
import pickle

from rltk.io.adapter import Adapter
from rltk.record import Record


class DBMAdapter(Adapter):
    def __init__(self, filename, dbm_class=dbm.ndbm):
        """
        :dbm_class dbm, dbm.gnu, dbm.ndbm, dbm.dumb (same as dbm)
        """
        self._db = dbm_class.open(filename, 'c')

        # not all dbm supports iterator, simulate an iterator by getting a key set
        # key will be in byte form once read out from dbm, needs to be converted to string
        self._ids = set([k.decode('utf-8') for k in self._db.keys()])

    def get(self, record_id):
        return pickle.loads(self._db.get(record_id))

    def set(self, record_id, record: Record):
        self._ids.add(record_id)
        self._db[record_id] = pickle.dumps(record)

    def __next__(self):
        for i in self._ids:
            yield self.get(i)

    def __del__(self):
        self._db.close()
