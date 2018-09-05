import io


class Reader(object):
    """
    Reader.
    """

    def __init__(self):
        pass

    def __iter__(self):
        """
        Same as :meth:`__next__`.
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator.
        
        Returns:
            iter: `raw_object`. The raw_object is a dict which represents raw data of a logical row.
        """
        raise NotImplementedError

    def __del__(self):
        """
        Same as :meth:`close`
        """

    def close(self):
        """
        Close handler.
        """
        pass
