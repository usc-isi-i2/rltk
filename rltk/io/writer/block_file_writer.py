import json
import os

from rltk.io.writer import BlockWriter


class BlockFileWriter(BlockWriter):
    def __init__(self, file_handler):
        self._file_handler = BlockWriter.get_file_handler(file_handler)

    def write(self, id1, id2s):
        self._file_handler.write(json.dumps({id1: id2s}) + '\n')

    def get_handler(self):
        return os.path.realpath(self._file_handler.name)

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
