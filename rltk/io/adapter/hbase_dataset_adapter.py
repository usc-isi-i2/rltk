import happybase

from rltk.record import Record
from rltk.io.adapter import DatasetAdapter
from rltk.io.serializer import Serializer, PickleSerializer


class HBaseDatasetAdapter(DatasetAdapter):
    """
    Hbase Adapter.
    
    Args:
        host (str): Host address.
        table (str): HBase table name.
        serializer (Serializer, optional): The serializer used to serialize Record object. 
                                If it's None, `PickleSerializer` will be used. Defaults to None.
        key_prefix (str, optional): The prefix of HBase row key.
        **kwargs: Other parameters used by `happybase.Connection <https://happybase.readthedocs.io/en/latest/api.html#connection>`_ .
    
    Note:
        The timeout of thrift in hbase-site.xml needs to increase::
        
            <property>
                <name>hbase.thrift.server.socket.read.timeout</name>
                <value>6000000</value>
            </property>
            <property>
                <name>hbase.thrift.connection.max-idletime</name>
                <value>18000000</value>
            </property>
    """

    def __init__(self, host, table, serializer: Serializer=None, key_prefix='', **kwargs):
        if not serializer:
            serializer = PickleSerializer()
        self._conn = happybase.Connection(host=host, timeout=None, **kwargs)
        self._serializer = serializer
        self._key_prefix = key_prefix
        self._family_name = 'rltk'
        self._col_name = 'obj'
        self._fam_col_name = '{}:{}'.format(self._family_name, self._col_name).encode('utf-8')

        if table.encode('utf-8') not in self._conn.tables():
            self._create_table(table)
        self._table = self._conn.table(table)

    #: parallel-safe
    parallel_safe = True

    def _get_key(self, record_id):
        return '{prefix}{record_id}'.format(prefix=self._key_prefix, record_id=record_id).encode('utf-8')

    def close(self):
        try:
            self._conn.close()
        except:
            pass

    def _create_table(self, table_name):
        self._conn.create_table(table_name, {self._family_name:dict()})

    def get(self, record_id) -> Record:
        return self._serializer.loads(self._table.row(self._get_key(record_id))[self._fam_col_name])

    def set(self, record_id, record: Record):
        return self._table.put(self._get_key(record_id), {self._fam_col_name: self._serializer.dumps(record)})

    def __next__(self):
        for key, data in self._table.scan(
                row_prefix=self._key_prefix.encode('utf-8'), filter=b'FirstKeyOnlyFilter()'):
            yield self._serializer.loads(data[self._fam_col_name])
