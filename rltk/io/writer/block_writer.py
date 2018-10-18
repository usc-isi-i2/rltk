from rltk.io.writer import Writer
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter
from rltk.blocking.block_generator import BlockDatasetID


class BlockWriter(Writer):
    """
    Block writer
    """
    def __init__(self, key_set_adapter: KeySetAdapter = None):
        super(BlockWriter, self).__init__()
        if not key_set_adapter:
            key_set_adapter = MemoryKeySetAdapter()
        self.key_set_adapter = key_set_adapter

    def write(self, block_id, dataset_id: BlockDatasetID, record_id):
        self.key_set_adapter.add(block_id, (dataset_id, record_id))

    # def get_blacklist(self):
    #     """
    #     Black list of indices.
    #     """
    #     if getattr(self, '_blacklist'):
    #         return self._blacklist
