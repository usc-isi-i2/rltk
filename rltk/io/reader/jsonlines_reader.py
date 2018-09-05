import json


from rltk.io.reader import Reader
from rltk.io.io_utils import get_file_handler


class JsonLinesReader(Reader):
    """
    `JSON Lines <http://jsonlines.org/>`_ Reader.
    
    Args:
        file_handler (str/io.IOBase): File name or file handler of input file.
        ignore_blank_line (bool): If blank line should be ignored. Defaults to True.
    """

    def __init__(self, file_handler, ignore_blank_line=True):
        self._file_handler = get_file_handler(file_handler)
        self._ignore_blank_line = ignore_blank_line

    def __next__(self):
        for line in self._file_handler:
            if line.strip() == '':
                if self._ignore_blank_line:
                    continue
                else:
                    raise ValueError('Blank line detected')
            yield json.loads(line)

    def close(self):
        try:
            self._file_handler.close()
        except:
            pass
