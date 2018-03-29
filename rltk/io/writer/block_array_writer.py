from rltk.io.writer import BlockWriter


class BlockArrayWriter(BlockWriter):
    def __init__(self):
        self._array = list()
        self._dict = dict()
        self._is_dirty = False

    def write(self, id1, id2):
        self._dict[id1] = self._dict.get(id1, set())
        s = self._dict[id1].add(id2)
        self._is_dirty = True

    def flush(self):
        if not self._is_dirty:
            return
        self._array = [{id1: list(id2s)} for id1, id2s in self._dict.items()]
        self._is_dirty = False

    def get_handler(self):
        self.flush()
        return self._array
