from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rltk.io.reader.block_reader import BlockReader
    from rltk.io.writer.block_writer import BlockWriter
from rltk.blocking.block_dataset_id import BlockDatasetID


class BlockingHelper(object):
    """
    It provides some useful blocking helper methods.
    
    Args:
        reader1 (BlockReader): BlockReader 1.
        reader2 (BlockReader): BlockReader 2.
    """

    def __init__(self, reader1, reader2):
        self._reader1 = reader1
        self._reader2 = reader2

    def union(self, writer):
        """
        Union two blocks.
        
        Args:
            writer (BlockWriter): Block writer.
        """

        for block_id, id1, id2 in self._reader1:
            writer.write(block_id, BlockDatasetID.Dataset1, id1)
            writer.write(block_id, BlockDatasetID.Dataset2, id2)
        for block_id, id1, id2 in self._reader2:
            writer.write(block_id, BlockDatasetID.Dataset1, id1)
            writer.write(block_id, BlockDatasetID.Dataset2, id2)
        writer.close()
