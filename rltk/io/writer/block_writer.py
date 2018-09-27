from rltk.io.writer import Writer


class BlockWriter(Writer):
    """
    Super class of block writer
    """

    def write(self, id1: str, id2: str):
        """
        Args:
            id1 (str): Record 1 id.
            id2 (str): Record 2 id.
        """
        raise NotImplementedError

    def get_handler(self):
        """
        The handler which can be used as input of corresponding :meth:`BlockReader`.
        """
        raise NotImplementedError

    def flush(self):
        """
        Force to flush buffer.
        """
        raise NotImplementedError

    def get_blacklist(self):
        """
        Black list of indices. 
        """
        if getattr(self, '_blacklist'):
            return self._blacklist

    def close(self):
        """
        Close handler.
        """
        self.flush()
        super().close()
