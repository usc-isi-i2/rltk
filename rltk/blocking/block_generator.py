from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.io.writer.block_writer import BlockWriter
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter


class BlockGenerator(object):
    """
    Block generator.
    """

    def block(self, dataset, function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None, block_max_size: int = -1, block_black_list: KeySetAdapter = None):
        """
        Block on property or by function for dataset.
        
        Args:
            dataset (Dataset): Dataset.
            function_ (Callable): `function_(r: record)`.
            property_ (str): The property in Record object.
            ks_adapter (KeySetAdapter): The adapter used to store blocks. 
                                    If None, `MemoryKeySetAdapter` is used. Defaults to None.
            block_max_size (int, optional): Size of the block. If a block is larger than this size, \
                                it will be added to black list. Defaults to -1.
            block_black_list (KeySetAdapter, optional): Where all blacklisted blocks are stored. Defaults to None.
                                    
        Returns:
            KeySetAdapter: The key set adapter.
        """
        ks_adapter = BlockGenerator._block_args_check(function_, property_, ks_adapter)
        return ks_adapter

    @staticmethod
    def _in_black_list(key: str, black_list: KeySetAdapter = None):
        if black_list:
            return black_list.get(key) is not None
        return False

    @staticmethod
    def _update_black_list(key: str, ks_adapter: KeySetAdapter,
                           block_max_size: int, black_list: KeySetAdapter):
        if block_max_size < 0 or not black_list:
            return
        size = len(ks_adapter.get(key))
        if size > block_max_size:
            ks_adapter.delete(key)
            black_list.set(key, set())

    @staticmethod
    def _block_args_check(function_, property_, ks_adapter):
        if not function_ and not property_:
            raise ValueError('Invalid function or property')
        if not ks_adapter:
            ks_adapter = MemoryKeySetAdapter()
        return ks_adapter

    def generate(self, ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
        """
        Generate blocks from two KeySetAdapters.
        
        Args:
            ks_adapter1 (KeySetAdapter): Key set adapter 1.
            ks_adapter2 (KeySetAdapter): Key set adapter 2.
            block_writer (BlockWriter): Block writer. If None, a new writer will be created. Defaults to None.
        
        Returns:
            KeySetAdapter: Key set adapter where block stores.
        """
        block_writer = BlockGenerator._generate_args_check(block_writer)
        return block_writer.key_set_adapter

    @staticmethod
    def _generate_args_check(block_writer):
        if not block_writer:
            block_writer = BlockWriter()
        return block_writer
