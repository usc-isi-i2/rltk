from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter
from rltk.blocking.block import Block


class BlockBlackList(object):
    def __init__(self, key_set_adapter: KeySetAdapter = None, max_size: int = 0):
        if not key_set_adapter:
            key_set_adapter = MemoryKeySetAdapter()
        self.key_set_adapter = key_set_adapter
        self._max_size = max_size

    def has(self, block_id: str):
        return self.key_set_adapter.get(block_id) is not None

    def add(self, block_id: str, block: Block):
        if self._max_size > 0:
            d = block.key_set_adapter.get(block_id)
            if len(d) > self._max_size:
                self.key_set_adapter.set(block_id, set())
                block.key_set_adapter.delete(block_id)
        else:
            self.key_set_adapter.set(block_id, set())

    def __contains__(self, item):
        self.has(item)
