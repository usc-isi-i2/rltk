import csv

from rltk.io.reader import Reader
from rltk.io.io_utils import get_file_handler


class CSVReader(Reader):
    """
    CSV reader.
    
    Args:
        file_handler (str/io.IOBase): File name or file handler of input file.
        **kwargs: Other parameters used by `csv.DictReader <https://docs.python.org/3/library/csv.html#csv.DictReader>`_ .
    """

    def __init__(self, file_handler, **kwargs):
        self._file_handler = get_file_handler(file_handler)
        self._csv_reader = csv.DictReader(self._file_handler, **kwargs)

    def __next__(self):
        for obj in self._csv_reader:
            yield {t[0]: t[1] for t in obj.items()}

    def close(self):
        try:
            self._file_handler.close()
        except:
            pass
