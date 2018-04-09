import json
import os

from rltk.io.writer import BlockWriter


class BlockFileWriter(BlockWriter):
    def __init__(self, filename, buffer_size=10000, set_size=1000, index_blacklist:set=None):
        self._filename = filename
        self._temp_filename = filename + '.temp'
        self._buffer_size = buffer_size
        self._dict = dict()
        self._set_size = set_size
        self._blacklist = index_blacklist or set()

    def write(self, id1, id2):
        # skip if id1 is in blacklist
        if id1 in self._blacklist:
            return

        # add pairs
        self._dict[id1] = self._dict.get(id1, set())
        self._dict[id1].add(id2)

        # update id1 to blacklist when reaching threshold and remove id1 in memory
        if len(self._dict[id1]) > self._set_size:
            self._blacklist.add(id1)
            del self._dict[id1]

        # flush when buffer is full
        if len(self._dict) >= self._buffer_size:
            self.flush()

    def get_handler(self):
        self.flush()
        return self._filename

    def flush(self):
        if len(self._dict) == 0:
            return

        # create empty file if it's not there
        if not os.path.exists(self._filename):
            open(self._filename, 'w').close()

        fp = open(self._filename, 'r')
        temp_fp = open(self._temp_filename, 'w')

        # concatenate old and new id2s
        for line in fp:
            old_obj = json.loads(line)
            if len(old_obj) != 1:
                raise TypeError('Invalid block file')

            id1 = list(old_obj.keys())[0]
            id2s = old_obj[id1]

            if id1 in self._blacklist:
                continue

            if id1 in self._dict:
                id2s = self._dict[id1] | set(id2s)
                del self._dict[id1]

            if len(id2s) >= self._set_size:
                self._blacklist.add(id1)
                # remove from buffer
                if id1 in self._dict:
                    del self._dict[id1]
                # remove from output
                continue

            temp_fp.write(json.dumps({id1: list(id2s)}) + '\n')

        # write new id1 and id2s
        for id1, id2s in self._dict.items():
            temp_fp.write(json.dumps({id1: list(id2s)}) + '\n')

        fp.close()
        temp_fp.close()
        self._dict = dict()

        # replace file
        os.remove(self._filename)
        os.rename(self._temp_filename, self._filename)
