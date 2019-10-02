from typing import Callable
from functools import cmp_to_key

from rltk.blocking.block_generator import BlockGenerator
from rltk.blocking.block import Block
from rltk.blocking.block_black_list import BlockBlackList


class SortedNeighbourhoodBlockGenerator(BlockGenerator):
    """
    Sorted Neighbourhood Blocker.
    
    Args:
        window_size (int): Window size.
        comparator (Callable): Define how to compare two tokens t1 and t2.
                            The signature is `comparator(t1: str, t2: str) -> int`.
                            If return is 0, t1 equals t2; if return is -1, t1 is less than t2;
                            if return is 1, t1 is greater than t2.
        block_id_prefix (str): The block id prefix of each block.
    """
    def __init__(self, window_size: int = 3, comparator: Callable = None, block_id_prefix='sorted_neighbourhood_'):
        if comparator is None:
            comparator = self._default_comparator
        self.window_size = window_size
        self.comparator = comparator
        self.block_id_prefix = block_id_prefix

    def block(self, dataset, function_: Callable = None, property_: str = None,
              block: Block = None, block_black_list: BlockBlackList = None, base_on: Block = None):
        """
        The return of `property_` or `function_` should be a vector (list).
        """
        block = super()._block_args_check(function_, property_, block)

        if base_on:
            for block_id, dataset_id, record_id in base_on:
                if dataset.id == dataset_id:
                    r = dataset.get_record(record_id)
                    value = function_(r) if function_ else getattr(r, property_)
                    if not isinstance(value, (list, set)):
                        value = value(set)
                    for v in value:
                        if not isinstance(v, str):
                            raise ValueError('Elements in return list should be string')
                        if block_black_list and block_black_list.has(v):
                            continue
                        v = block_id + '-' + v
                        block.add(v, dataset.id, r.id)
                        if block_black_list:
                            block_black_list.add(v, block)

        else:
            for r in dataset:
                value = function_(r) if function_ else getattr(r, property_)
                if not isinstance(value, (list, set)):
                    value = set(value)
                for v in value:
                    if not isinstance(v, str):
                        raise ValueError('Elements in return list should be string')
                    if block_black_list and block_black_list.has(v):
                        continue
                    block.add(v, dataset.id, r.id)
                    if block_black_list:
                        block_black_list.add(v, block)

        return block

    def generate(self, block1: Block, block2: Block, output_block: Block = None):
        output_block = BlockGenerator._generate_args_check(output_block)

        # TODO: in-memory operations here, need to update
        # concatenation
        all_records = []
        for block_id, ds_id, record_id in block1:
            all_records.append((block_id, ds_id, record_id))
        for block_id, ds_id, record_id in block2:
            all_records.append((block_id, ds_id, record_id))
        sorted_all_records = sorted(all_records, key=cmp_to_key(self._comparator_wrapper))

        # apply slide window
        for i in range(len(sorted_all_records) - self.window_size + 1):
            block_id = self.block_id_prefix + str(i)
            for j in range(self.window_size):
                record = sorted_all_records[i + j]
                output_block.add(block_id, record[1], record[2])

        return output_block

    def _comparator_wrapper(self, t1, t2):
        return self.comparator(t1[0], t2[0])

    @staticmethod
    def _default_comparator(t1, t2):
        return 0 if t1 == t2 else (1 if t1 > t2 else -1)
