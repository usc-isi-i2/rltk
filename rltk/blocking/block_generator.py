from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from rltk.dataset import Dataset
from rltk.blocking.block import Block
from rltk.blocking.block_black_list import BlockBlackList


class BlockGenerator(object):
    """
    Block generator.
    """

    def block(self, dataset: 'Dataset', function_: Callable = None, property_: str = None,
              block: Block = None, block_black_list: BlockBlackList = None):
        """
        Block on property or by function for dataset.
        
        Args:
            dataset (Dataset): Dataset.
            function_ (Callable): `function_(r: record)`.
            property_ (str): The property in Record object.
            block (Block): Where to write blocks. If None, a new block will be created. Defaults to None.
            block_black_list (BlockBlackList, optional): Where all blacklisted blocks are stored. Defaults to None.
                                    
        Returns:
            Block: 
        """
        block = BlockGenerator._block_args_check(function_, property_, block)
        return block

    @staticmethod
    def _block_args_check(function_, property_, block):
        if not function_ and not property_:
            raise ValueError('Invalid function or property')
        return block or Block()

    def generate(self, block1: Block, block2: Block, output_block: Block = None):
        """
        Generate blocks from two KeySetAdapters.
        
        Args:
            block1 (Block): Block 1.
            block2 (Block): Block 2.
            output_block (Block): Where the output block goes. If None, a new block will be created. Defaults to None.
        
        Returns:
            Block:
        """
        block = BlockGenerator._generate_args_check(output_block)
        return block

    @staticmethod
    def _generate_args_check(block):
        return block or Block()
