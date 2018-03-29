import csv

from rltk.io.reader import Reader


class GroundTruthReader(Reader):

    def __init__(self, file_handler, **kwargs):
        self._file_handler = Reader.get_file_handler(file_handler)
        self._csv_reader = csv.DictReader(self._file_handler, **kwargs)

    def __next__(self):
        for obj in self._csv_reader:
            yield {t[0]: t[1] for t in obj.items()}

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
