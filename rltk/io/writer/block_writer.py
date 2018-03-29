from rltk.io.writer import Writer


class BlockWriter(Writer):
    def write(self, id1, id2):
        raise NotImplementedError

    def get_handler(self):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def close(self):
        self.flush()
        super().close()
