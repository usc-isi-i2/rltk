import csv
import codecs

from rltk.io.reader import Reader


class CSVReader(Reader):

    def __init__(self, filename, **kwargs):
        self._filename = filename
        self._kwargs = kwargs
        self._loop_count = 0

        self._file_handler = codecs.open(filename)
        self._csv_reader = csv.DictReader(self._file_handler, **kwargs)

    def __next__(self):
        for obj in self._csv_reader:
            self._loop_count += 1
            yield {t[0]: t[1] for t in obj.items()}

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass

    def __copy__(self):
        new_reader = CSVReader(self._filename, **self._kwargs)
        while new_reader._loop_count < self._loop_count:
            new_reader.__next__()
        return new_reader
