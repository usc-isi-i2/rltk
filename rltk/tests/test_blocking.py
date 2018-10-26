import pytest

from rltk.record import Record
from rltk.dataset import Dataset
from rltk.io.reader.array_reader import ArrayReader
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter
from rltk.blocking.hash_block_generator import HashBlockGenerator
from rltk.blocking.token_block_generator import TokenBlockGenerator
from rltk.blocking.canopy_block_generator import CanopyBlockGenerator


class ConcreteRecord(Record):
   @property
   def id(self):
       return self.raw_object['id']

   @property
   def name(self):
       return self.raw_object['name']

   @property
   def category(self):
       return self.raw_object['category']


raw_data = [
    {'id': '1', 'name': 'apple', 'category': 'a'},
    {'id': '2', 'name': 'banana', 'category': 'a'},
    {'id': '3', 'name': 'apple & banana', 'category': 'b'},
    {'id': '4', 'name': 'pineapple', 'category': 'b'},
    {'id': '5', 'name': 'peach', 'category': 'b'},
    {'id': '6', 'name': 'coconut', 'category': 'b'}
]

ds = Dataset(reader=ArrayReader(raw_data), record_class=ConcreteRecord)


def test_hash_block_generator():
    bg = HashBlockGenerator()
    ks_adapter = bg.block(ds, property_='category')
    for key, set_ in ks_adapter:
        if key == 'a':
            assert set_ == set(['1', '2'])
        elif key == 'b':
            assert set_ == set(['3', '4', '5', '6'])
    ks_adapter = bg.block(ds, function_=lambda r: r.category)
    for key, set_ in ks_adapter:
        if key == 'a':
            assert set_ == set(['1', '2'])
        elif key == 'b':
            assert set_ == set(['3', '4', '5', '6'])

    black_list = MemoryKeySetAdapter()
    ks_adapter = bg.block(ds, property_='category', block_max_size=2, block_black_list=black_list)
    for key, set_ in ks_adapter:
        assert key == 'a'
    for key, _ in black_list:
        assert key == 'b'


def test_token_block_generator():
    bg = TokenBlockGenerator()
    ks_adapter = bg.block(ds, function_=lambda r: r.name.split(' '))
    for key, set_ in ks_adapter:
        if key == 'apple':
            assert set_ == set(['1', '3'])
        elif key == 'banana':
            assert set_ == set(['2', '3'])

    black_list = MemoryKeySetAdapter()
    ks_adapter = bg.block(ds, function_=lambda r: r.name.split(' '), block_max_size=1, block_black_list=black_list)
    for key, set_ in ks_adapter:
        assert len(set_) <= 1
    for key, _ in black_list:
        assert key in ('apple', 'banana')


def test_canopy_block_generator():
    bg = CanopyBlockGenerator(t1=5, t2=1, distance_metric=lambda x, y: abs(x[0] - y[0]))
    ks_adapter = bg.block(ds, function_=lambda r: [ord(r.name[0].lower()) - 0x61])
    result = bg.generate(ks_adapter, ks_adapter)
    for k, v in result:
        assert k in ('[1]', '[2]', '[0]', '[15]')
