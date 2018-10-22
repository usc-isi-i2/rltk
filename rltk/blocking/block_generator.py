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

    @staticmethod
    def block(dataset, function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None):
        """
        Block on property or by function for dataset.
        
        Args:
            dataset (Dataset): Dataset.
            function_ (Callable): `function_(r: record)`.
            property_ (str): The property in Record object.
            ks_adapter (KeySetAdapter): The adapter used to store blocks. 
                                    If None, `MemoryKeySetAdapter` is used. Defaults to None.
                                    
        Returns:
            KeySetAdapter: The key set adapter.
        """
        ks_adapter = BlockGenerator._block_args_check(function_, property_, ks_adapter)
        return ks_adapter

    @staticmethod
    def _block_args_check(function_, property_, ks_adapter):
        if not function_ and not property_:
            raise ValueError('Invalid function or property')
        if not ks_adapter:
            ks_adapter = MemoryKeySetAdapter()
        return ks_adapter

    @staticmethod
    def generate(ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
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
