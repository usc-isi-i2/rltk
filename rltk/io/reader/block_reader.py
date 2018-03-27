from rltk.io.reader import Reader


class BlockReader(Reader):
    def __next__(self):
        raise NotImplementedError
