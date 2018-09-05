import sys

from rltk.io.writer import BlockWriter


class BlockArrayWriter(BlockWriter):
    """
    Block writer stores data in array (list).
    
    Args:
        set_size (int, optional): Maximum size of a block. Defaults to `sys.maxsize`.
        index_blacklist (set, optional): If a Record's id is in blacklist, it won't be in output. Default's to None.
    """
    def __init__(self, set_size: int = sys.maxsize, index_blacklist: set = None):
        self._array = list()
        self._dict = dict()
        self._is_dirty = False
        self._set_size = set_size
        self._blacklist = index_blacklist or set()

    def write(self, id1: str, id2: str):
        if id1 in self._blacklist:
            return

        self._dict[id1] = self._dict.get(id1, set())
        s = self._dict[id1].add(id2)
        self._is_dirty = True

        if len(self._dict[id1]) > self._set_size:
            self._blacklist.add(id1)
            del self._dict[id1]

    def flush(self):
        if not self._is_dirty:
            return
        self._array = [{id1: list(id2s)} for id1, id2s in self._dict.items()]
        self._is_dirty = False

    def get_handler(self):
        self.flush()
        return self._array
