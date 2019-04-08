from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.blocking.block_generator import BlockGenerator
from rltk.blocking.block import Block
from rltk.blocking.block_black_list import BlockBlackList


class HashBlockGenerator(BlockGenerator):
    """
    Hash block generator.
    """

    def block(self, dataset, function_: Callable = None, property_: str = None,
              block: Block = None, block_black_list: BlockBlackList = None, base_on: Block = None):
        """
        The return of `property_` or `function_` should be string.
        """
        block = super()._block_args_check(function_, property_, block)

        if base_on:
            for block_id, dataset_id, record_id in base_on:
                if dataset.id == dataset_id:
                    r = dataset.get_record(record_id)
                    value = function_(r) if function_ else getattr(r, property_)
                    if not isinstance(value, str):
                        raise ValueError('Return of the function or property should be a string')
                    value = block_id + '-' + value
                    if block_black_list and block_black_list.has(value):
                        continue
                    block.add(value, dataset.id, r.id)
                    if block_black_list:
                        block_black_list.add(value, block)

        else:
            for r in dataset:
                value = function_(r) if function_ else getattr(r, property_)
                if not isinstance(value, str):
                    raise ValueError('Return of the function or property should be a string')
                if block_black_list and block_black_list.has(value):
                    continue
                block.add(value, dataset.id, r.id)
                if block_black_list:
                    block_black_list.add(value, block)

        return block

    def generate(self, block1: Block, block2: Block, output_block: Block = None):
        output_block = super()._generate_args_check(output_block)
        for block_id, ds_id, record_id in block1:
                output_block.add(block_id, ds_id, record_id)
        for block_id, ds_id, record_id in block2:
                output_block.add(block_id, ds_id, record_id)
        return output_block
