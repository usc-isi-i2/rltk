from rltk.io.writer import BlockWriter


class BlockArrayWriter(BlockWriter):
    def __init__(self, array):
        if array is None:
            array = list()
        if not isinstance(array, list):
            raise TypeError('Type of array should be list.')
        self._array = array

    def write(self, id1, id2s):
        self._array.append({id1: id2s})

    def get_handler(self):
        return self._array
