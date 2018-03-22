from rltk.io.reader import Reader


class BlockReader(Reader):

    def __init__(self, raw_blocks):
        self._raw_blocks = raw_blocks

    def __next__(self):
        for block in self._raw_blocks: # iterate json objects
            for id1, id2s in block.items(): # iterate on one json object
                for id2 in id2s:
                    yield id1, id2

    def __del__(self):
        pass
