from rltk.io.reader import Reader


class ArrayReader(Reader):
    """
    Array Reader.
    
    Args:
        array (list): Array.
    """

    def __init__(self, array):
        try:
            for _ in array:
                break
        except TypeError:
            raise TypeError('Can not iterate on ArrayReader')

        self._array = array

    def __next__(self):
        for item in self._array:
            yield item

