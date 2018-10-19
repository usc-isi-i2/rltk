from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.io.writer.block_writer import BlockWriter
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class BlockGenerator(object):

    @staticmethod
    def block(dataset: 'Dataset', function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None):
        raise NotImplementedError
        # return KeySetAdapter

    @staticmethod
    def generate(ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
        raise NotImplementedError
        # return KeySetAdapter
