from rltk.io.writer.block_writer import BlockWriter
from rltk.dataset import Dataset


class BlockGenerator(object):
    """
    Super class of block generator
    
    Args:
        dataset1 (Dataset): Dataset 1.
        dataset2 (Dataset): Dataset 2.
        writer (BlockWriter): Block writer.
        **kwargs: Key word arguments used by concrete class.
    """

    def __init__(self, dataset1: Dataset, dataset2: Dataset, writer: BlockWriter, **kwargs):
        self._writer = writer
        self._dataset1 = dataset1
        self._dataset2 = dataset2
        self._kwargs = kwargs

    def generate(self):
        """
        Generate blocks (:meth:`_generate_blocks`) and return handler.
        
        Returns:
            obj: Writer handler, which can be used by corresponding Reader.
            
        """

        self._generate_blocks()

        handler = self._writer.get_handler()
        self._writer.close()
        return handler

    def _generate_blocks(self):
        """
        Generate blocks. It needs to be overwritten.
        """
        raise NotImplementedError
