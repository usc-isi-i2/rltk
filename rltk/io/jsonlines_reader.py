import json
import codecs

from rltk.io.reader import Reader


class JsonLinesReader(Reader):

    def __init__(self, filename, ignore_blank_line=True):
        self._filename = filename
        self._loop_count = 0

        self._file_handler = codecs.open(filename)
        self._ignore_blank_line = ignore_blank_line

    def __next__(self):
        for line in self._file_handler:
            if line.strip() == '':
                if self._ignore_blank_line:
                    continue
                else:
                    raise ValueError('Blank line detected')
            self._loop_count += 1
            yield json.loads(line)

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass

    def __copy__(self):
        new_reader = JsonLinesReader(self._filename, self._ignore_blank_line)
        while new_reader._loop_count < self._loop_count:
            new_reader.__next__()
        return new_reader
