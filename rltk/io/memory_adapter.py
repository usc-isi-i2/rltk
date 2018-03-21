from rltk.io.adapter import Adapter
from rltk.record import Record


class MemoryAdapter(Adapter):
    def __init__(self):
        self._records = dict()

    def get(self, record_id):
        return self._records.get(record_id)

    def set(self, record_id, record: Record):
        self._records[record_id] = record
