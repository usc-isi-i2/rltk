from rltk.io.writer import Writer


class BlockWriter(Writer):
    """
    index: sets
    black list is on index
    """

    def write(self, id1, id2):
        raise NotImplementedError

    def get_handler(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def get_blacklist(self):
        return self._blacklist

    def close(self):
        self.flush()
        super().close()
