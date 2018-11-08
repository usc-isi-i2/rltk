from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.io.reader.block_reader import BlockReader
from rltk.io.writer.block_writer import BlockWriter
from rltk.blocking.block_generator import BlockGenerator
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class HashBlockGenerator(BlockGenerator):
    """
    Hash block generator.
    """

    def block(self, dataset, ds_id: str, function_: Callable = None, property_: str = None,
              block_writer: BlockWriter = None, block_max_size: int = -1, block_black_list: KeySetAdapter = None):
        """
        The return of `property_` or `function_` should be string.
        """
        block_writer = super()._block_args_check(function_, property_, block_writer)
        for r in dataset:
            value = function_(r) if function_ else getattr(r, property_)
            if self._in_black_list(value, block_black_list):
                continue
            if not isinstance(value, str):
                raise ValueError('Return of the function or property should be a string')
            block_writer.write(value, ds_id, r.id)
            self._update_black_list(value, block_writer.key_set_adapter, block_max_size, block_black_list)
        return block_writer.key_set_adapter

    def generate(self, block_reader1: BlockReader, block_reader2: BlockReader, block_writer: BlockWriter = None):
        block_writer = super()._generate_args_check(block_writer)
        for block_id, ds_id, record_id in block_reader1:
                block_writer.write(block_id, ds_id, record_id)
        for block_id, ds_id, record_id in block_reader2:
                block_writer.write(block_id, ds_id, record_id)
        return block_writer.key_set_adapter
