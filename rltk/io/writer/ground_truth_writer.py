import csv

from rltk.io.writer import Writer


class GroundTruthWriter(Writer):
    def __init__(self, file_handler):
        self._file_handler = Writer.get_file_handler(file_handler)
        fieldnames = ['id1', 'id2', 'label']
        self._csv_writer = csv.DictWriter(self._file_handler, fieldnames=fieldnames)
        self._csv_writer.writeheader()

    def write(self, id1 : str, id2 : str, label : int):
        self._csv_writer.writerow({'id1': id1, 'id2': id2, 'label': label})

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
