from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.io.writer.block_writer import BlockWriter
from rltk.blocking.block_generator import BlockGenerator
from rltk.blocking.block_dataset_id import BlockDatasetID
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class HashBlockGenerator(BlockGenerator):
    """
    Hash block generator.
    """

    @staticmethod
    def block(dataset, function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None):
        """
        The return of `property_` or `function_` should be string.
        """
        ks_adapter = BlockGenerator._block_args_check(function_, property_, ks_adapter)
        for r in dataset:
            value = function_(r) if function_ else getattr(r, property_)
            if not isinstance(value, str):
                raise ValueError('Return of the function or property should be a string')
            ks_adapter.add(value, r.id)
        return ks_adapter

    @staticmethod
    def generate(ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
        block_writer = BlockGenerator._generate_args_check(block_writer)
        for block_id, id1s in ks_adapter1:
            for id1 in id1s:
                block_writer.write(block_id, BlockDatasetID.Dataset1, id1)
        for block_id, id2s in ks_adapter2:
            for id2 in id2s:
                block_writer.write(block_id, BlockDatasetID.Dataset2, id2)
        return block_writer.key_set_adapter
