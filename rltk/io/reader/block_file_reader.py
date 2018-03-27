import json

from rltk.io.reader import Reader


class BlockFileReader(Reader):

    def __init__(self, file_handler):
        self._file_handler = Reader.get_file_handler(file_handler)

    def __next__(self):
        for obj in self._file_handler: # iterate json objects
            block = json.loads(obj)
            for id1, id2s in block.items(): # iterate on one json object
                for id2 in id2s:
                    yield id1, id2

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
