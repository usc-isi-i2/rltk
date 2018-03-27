from rltk.io.adapter import KeyValueAdapter
from rltk.record import Record


class MemoryAdapter(KeyValueAdapter):
    def __init__(self):
        self._records = dict()

    def get(self, record_id):
        return self._records.get(record_id)

    def set(self, record_id, record: Record):
        self._records[record_id] = record

    def __next__(self):
        for r in self._records.values():
            yield r
