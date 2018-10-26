from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.io.writer.block_writer import BlockWriter
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.blocking.block_generator import BlockGenerator
from rltk.blocking.block_dataset_id import BlockDatasetID


class TokenBlockGenerator(BlockGenerator):
    """
    Token block generator. The return for :meth:`block` should be a `list` or `set`.
    """

    def block(self, dataset, function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None, block_max_size: int = -1, block_black_list: KeySetAdapter = None):
        """
        The return of `property_` or `function_` should be list or set.
        """
        ks_adapter = super()._block_args_check(function_, property_, ks_adapter)
        for r in dataset:
            value = function_(r) if function_ else getattr(r, property_)
            if not isinstance(value, list) and not isinstance(value, set):
                raise ValueError('Return of the function or property should be a list')
            for v in value:
                if self._in_black_list(v, block_black_list):
                    continue
                if not isinstance(v, str):
                    raise ValueError('Elements in return list should be string')
                ks_adapter.add(v, r.id)
                self._update_black_list(v, ks_adapter, block_max_size, block_black_list)
        return ks_adapter

    def generate(self, ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
        block_writer = super()._generate_args_check(block_writer)
        for block_id, id1s in ks_adapter1:
            for id1 in id1s:
                block_writer.write(block_id, BlockDatasetID.Dataset1, id1)
        for block_id, id2s in ks_adapter2:
            for id2 in id2s:
                block_writer.write(block_id, BlockDatasetID.Dataset2, id2)
        return block_writer.key_set_adapter

