from rltk.io.reader.block_reader import BlockReader
from rltk.io.writer.block_writer import BlockWriter


class BlockingHelper(object):
    """
    It provides some useful blocking helper methods.
    
    Args:
        reader1 (BlockReader): BlockReader 1.
        reader2 (BlockReader): BlockReader 2.
    """

    def __init__(self, reader1: BlockReader, reader2: BlockReader):
        self._reader1 = reader1
        self._reader2 = reader2

    def union(self, writer: BlockWriter):
        """
        Union two blocks.
        
        Args:
            writer (BlockWriter): Block writer.
        """

        for id1, id2 in self._reader1:
            writer.write(id1, id2)
        for id1, id2 in self._reader2:
            writer.write(id1, id2)
        writer.close()
