import os
import pytest
import redis
import tempfile
import shutil

from rltk.record import Record
from rltk.io.adapter import *


class ConcreteRecord(Record):

    @property
    def id(self):
        return self.raw_object['id']

    @property
    def value(self):
        return self.raw_object['value']

record = ConcreteRecord(raw_object={'id': 'id1', 'value': 'value1'})


def _test_key_value_adapter(adapter):
    adapter.set(record.id, record)
    assert adapter.get(record.id).id == record.id
    assert adapter.get(record.id).value == record.value
    for rid, r in adapter:
        assert type(rid) == str
        assert rid == record.id
        assert r.id == record.id
        break

    assert adapter.get('no_such_key') is None


def test_memory_key_value_adapter():
    adapter = MemoryKeyValueAdapter()
    _test_key_value_adapter(adapter)


def test_dbm_key_value_adapter():
    name = 'test_dbm_adapter'
    adapter = DbmKeyValueAdapter(name)
    _test_key_value_adapter(adapter)
    if os.path.exists(name + '.db'):
        os.remove(name + '.db')


def test_redis_key_value_adapter():
    try:
        adapter = RedisKeyValueAdapter('127.0.0.1', key_prefix='test_')
        _test_key_value_adapter(adapter)
    except redis.exceptions.ConnectionError:
        return


def _test_key_set_adapter(adapter):
    adapter.set('a', set(['1', '2', '3']))
    assert adapter.get('a') == set(['1', '2', '3'])
    adapter.add('a', '4')
    assert adapter.get('a') == set(['1', '2', '3', '4'])
    adapter.remove('a', '4')
    assert adapter.get('a') == set(['1', '2', '3'])
    assert adapter.get('b') is None
    for k, v in adapter:
        assert type(k) == str
        assert k == 'a'
        assert v == set(['1', '2', '3'])
        break
    adapter.delete('a')
    assert adapter.get('a') is None
    adapter.set('c', set(['1', '2', '3']))
    adapter.clean()
    assert adapter.get('c') is None


def test_memory_key_set_adapter():
    adapter = MemoryKeySetAdapter()
    _test_key_set_adapter(adapter)


def test_leveldb_key_set_adapter():
    path = os.path.join(tempfile.gettempdir(), 'rltk_test_leveldb_key_set_adapter')
    adapter = LevelDbKeySetAdapter(path, name='test')
    _test_key_set_adapter(adapter)

    shutil.rmtree(path)


def test_redis_key_set_adapter():
    try:
        adapter = RedisKeySetAdapter('127.0.0.1', key_prefix='rltk_test_redis_key_set_adapter_')
        _test_key_set_adapter(adapter)
    except redis.exceptions.ConnectionError:
        return
