from rltk.io.writer import Writer


class BlockWriter(Writer):
    def write(self, id1, id2s):
        raise NotImplementedError

    def get_handler(self):
        raise NotImplementedError
