import io


class Writer(object):
    """
    Writer.
    """
    def __init__(self):
        pass

    def write(self):
        """
        Write content.
        """
        raise NotImplementedError

    def __del__(self):
        """
        Same to :meth:`close`.
        """
        self.close()

    def close(self):
        """
        Close handler.
        """
        pass
