import happybase

from rltk.record import Record
from rltk.io.adapter import KeyValueAdapter
from rltk.io.serializer import Serializer, PickleSerializer


class HBaseAdapter(KeyValueAdapter):
    def __init__(self, host, table, serializer: Serializer=None, key_format='{record_id}', **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._conn = happybase.Connection(host=host, **kwargs)
        self._serializer = serializer
        self._key_format = key_format
        self._family_name = 'rltk'
        self._col_name = 'obj'
        if bytes(table, 'utf-8') not in self._conn.tables():
            self._create_table(table)
        self._table = self._conn.table(table)

        try:
            self._get_key('test_id')
        except:
            raise ValueError('Invalid key_format.')

    def _get_key(self, record_id):
        return bytes(self._key_format.format(record_id=record_id), 'utf-8')

    def __del__(self):
        try:
            self._conn.close()
        except:
            pass

    def _create_table(self, table_name):
        self._conn.create_table(table_name, {bytes(self._family_name, 'utf-8'):dict()})

    def get(self, record_id) -> Record:
        col = bytes('{}:{}'.format(self._family_name, self._col_name), 'utf-8')
        return self._serializer.loads(self._table.rows(self._get_key(record_id))[col])

    def set(self, record_id, record: Record):
        col = bytes('{}:{}'.format(self._family_name, self._col_name), 'utf-8')
        return self._table.put(self._get_key(record_id), {col: self._serializer.dumps(record)})

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        col = bytes('{}:{}'.format(self._family_name, self._col_name), 'utf-8')
        for key, data in self._table.scan(self._get_key('*')):
            yield self._serializer.loads(data[col])
