import os
import pytest
import redis

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


def test_memory_adapter():
    adapter = MemoryDatasetAdapter()
    adapter.set(record.id, record)
    assert adapter.get(record.id).id == record.id
    assert adapter.get(record.id).value == record.value
    for r in adapter:
        assert r.id == record.id
        break


def test_dbm_adapter():
    name = 'test_dbm_adapter'
    adapter = DbmDatasetAdapter(name)
    adapter.set(record.id, record)
    assert adapter.get(record.id).id == record.id
    assert adapter.get(record.id).value == record.value
    for r in adapter:
        assert r.id == record.id
        break
    if os.path.exists(name + '.db'):
        os.remove(name + '.db')


def test_redis_adapter():
    try:
        adapter = RedisDatasetAdapter('127.0.0.1', key_format='test_{record_id}')
        adapter.set(record.id, record)
        assert adapter.get(record.id).id == record.id
        assert adapter.get(record.id).value == record.value
        for r in adapter:
            assert r.id == record.id
            break

    except redis.exceptions.ConnectionError:
        return
