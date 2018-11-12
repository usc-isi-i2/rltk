from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter
from rltk.blocking.block import Block


class BlockBlackList(object):
    """
    Block black list
    
    Args:
        key_set_adapter (keySetAdapter, optional): Where the block stores. If it's None, 
                                            :meth:`MemoryKeySetAdapter` is used. Defaults to None.
        max_size (int, optional): Maximum size of a block. Used by :meth:`add`. Defaults to 0.
    """
    def __init__(self, key_set_adapter: KeySetAdapter = None, max_size: int = 0):
        if not key_set_adapter:
            key_set_adapter = MemoryKeySetAdapter()
        self.key_set_adapter = key_set_adapter
        self._max_size = max_size

    def has(self, block_id: str):
        """
        Test if block_id is in black list.
        
        Args:
            block_id (str): Block id.
        """
        return self.key_set_adapter.get(block_id) is not None

    def add(self, block_id: str, block: Block):
        """
        Add block_id to black list and update block data.
        
        Args:
            block_id (str): Block id.
            block (Block): Block object.
            
        Notes:
            * If `max_size` is 0, then block_id will be added.
            * If `max_size` is greater than 0 and data in this block is more than this size,
                this block_id will be added to BlockBlackList and this block is removed from Block.
        """
        if self._max_size > 0:
            d = block.key_set_adapter.get(block_id)
            if len(d) > self._max_size:
                self.key_set_adapter.set(block_id, set())
                block.key_set_adapter.delete(block_id)
        else:
            self.key_set_adapter.set(block_id, set())

    def __contains__(self, item):
        """
        Same as :meth:`has`
        """
        self.has(item)
