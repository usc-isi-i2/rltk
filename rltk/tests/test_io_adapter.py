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


def _test_dataset_adapter(adapter):
    adapter.set(record.id, record)
    assert adapter.get(record.id).id == record.id
    assert adapter.get(record.id).value == record.value
    for r in adapter:
        assert r.id == record.id
        break


def test_memory_dataset_adapter():
    adapter = MemoryDatasetAdapter()
    _test_dataset_adapter(adapter)


def test_dbm_dataset_adapter():
    name = 'test_dbm_adapter'
    adapter = DbmDatasetAdapter(name)
    _test_dataset_adapter(adapter)
    if os.path.exists(name + '.db'):
        os.remove(name + '.db')


def test_redis_dataset_adapter():
    try:
        adapter = RedisDatasetAdapter('127.0.0.1', key_format='test_{record_id}')
        _test_dataset_adapter(adapter)
    except redis.exceptions.ConnectionError:
        return


def _test_key_set_adapter(adapter):
    adapter.set('a', set(['1', '2', '3']))
    assert adapter.get('a') == set(['1', '2', '3'])
    adapter.add('a', '4')
    assert adapter.get('a') == set(['1', '2', '3', '4'])
    adapter.remove('a', '4')
    assert adapter.get('a') == set(['1', '2', '3'])
    for k, v in adapter:
        assert k == 'a'
        assert v == set(['1', '2', '3'])
        break
    adapter.delete('a')
    assert adapter.get('a') is None


def test_memory_key_set_adapter():
    adapter = MemoryKeySetAdapter()
    _test_key_set_adapter(adapter)


def test_leveldb_key_set_adapter():
    path = os.path.join(tempfile.tempdir, 'rltk_test_leveldb_key_set_adapter')
    adapter = LevelDbKeySetAdapter(path, name='test')
    _test_key_set_adapter(adapter)
    shutil.rmtree(path)


def test_redis_key_set_adapter():
    try:
        adapter = RedisDatasetAdapter('127.0.0.1', key_format='rltk_test_redis_key_set_adapter_{record_id}')
        _test_dataset_adapter(adapter)
    except redis.exceptions.ConnectionError:
        return
