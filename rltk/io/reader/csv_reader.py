import csv
import codecs

from rltk.io.reader import Reader


class CSVReader(Reader):

    def __init__(self, filename, **kwargs):
        self._file_handler = codecs.open(filename)
        self._csv_reader = csv.DictReader(self._file_handler, **kwargs)

    def __next__(self):
        for obj in self._csv_reader:
            yield {t[0]: t[1] for t in obj.items()}

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
