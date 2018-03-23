import json

from rltk.io.reader import Reader


class JsonLinesReader(Reader):

    def __init__(self, file_handler, ignore_blank_line=True):
        self._file_handler = file_handler
        self._ignore_blank_line = ignore_blank_line

    def __next__(self):
        for line in self._file_handler:
            if line.strip() == '':
                if self._ignore_blank_line:
                    continue
                else:
                    raise ValueError('Blank line detected')
            yield json.loads(line)

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
