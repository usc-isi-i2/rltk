from rltk.io.reader import BlockReader


class BlockArrayReader(BlockReader):
    """
    Block reader which input is an array.
    
    Args:
        array (list): A Python list which stores blocks.
    """

    def __init__(self, array):
        if not isinstance(array, list):
            raise TypeError('Type of array should be list.')
        self._array = array

    def __next__(self):
        for block in self._array: # iterate json objects
            for id1, id2s in block.items(): # iterate on one json object
                for id2 in id2s:
                    yield id1, id2
