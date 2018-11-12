import json
import hashlib
import operator

from rltk.blocking.block import Block
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter


class BlockingHelper(object):
    """
    Blocking Helper.
    """

    @staticmethod
    def encode_inverted_index_key(dataset_id, record_id):
        return json.dumps({'d': dataset_id, 'r': record_id}, sort_keys=True)

    @staticmethod
    def decode_inverted_index_key(key):
        key = json.loads(key)
        return key['d'], key['r']

    @staticmethod
    def generate_inverted_indices(block: Block, ks_adapter: KeySetAdapter = None):
        """
        Generate inverted indices of block.
        
        Args:
            block (Block): Original block.
            ks_adapter (KeySetAdapter): Where the inverted indices store.
            
        Returns:
            KeySetAdapter:
        """
        if not ks_adapter:
            ks_adapter = MemoryKeySetAdapter()
        for block_id, dataset_id, record_id in block:
            ks_adapter.add(BlockingHelper.encode_inverted_index_key(dataset_id, record_id), block_id)
        return ks_adapter

    @staticmethod
    def _block_operations(operator_, left_block, right_block, right_inverted, output_block):
        operation = None
        if operator_ == 'union':
            operation = operator.or_  # lambda a, b: a | b
        elif operator_ == 'intersect':
            operation = operator.and_  # lambda a, b: a & b

        for left_block_id, left_data in left_block.key_set_adapter:
            for left_dataset_id, left_record_id in left_data:
                key = BlockingHelper.encode_inverted_index_key(left_dataset_id, left_record_id)
                right_block_ids = right_inverted.get(key)
                if right_block_ids:
                    for right_block_id in right_block_ids:
                        new_block_data = operation(left_data, right_block.get(right_block_id))
                        new_block_id = hashlib \
                            .sha1(''.join(sorted(['{},{}'.format(ds, r) for ds, r in new_block_data]))
                                  .encode('utf-8')).hexdigest()
                        output_block.key_set_adapter.set(new_block_id, new_block_data)

    @staticmethod
    def union(block1, inverted1, block2, inverted2, block3=None):
        """
        Union of two blocks.
        
        Args:
            block1 (Block): Block 1.
            inverted1 (KeySetAdapter): Inverted indices of block 1.
            block2 (Block): Block2.
            inverted2 (KeySetAdapter): Inverted indices of block 2.
            block3 (Block, optional): Unioned block. If None, a Block object will be created. Defaults to None. 
        
        Returns:
            Block:
        """
        block3 = block3 or Block()

        BlockingHelper._block_operations('union', block1, block2, inverted2, block3)
        BlockingHelper._block_operations('union', block2, block1, inverted1, block3)
        return block3

    @staticmethod
    def intersect(block1, inverted1, block2, inverted2, block3=None):
        """
        Intersection of two blocks.
        
        Args:
            block1 (Block): Block 1.
            inverted1 (KeySetAdapter): Inverted indices of block 1.
            block2 (Block): Block2.
            inverted2 (KeySetAdapter): Inverted indices of block 2.
            block3 (Block, optional): Intersected block. If None, a Block object will be created. Defaults to None. 
        
        Returns:
            Block:
        """
        block3 = block3 or Block()

        BlockingHelper._block_operations('intersect', block1, block2, inverted2, block3)
        BlockingHelper._block_operations('intersect', block2, block1, inverted1, block3)
        return block3
