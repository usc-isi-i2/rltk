import csv

from rltk.io.writer import Writer
from rltk.io.io_utils import get_file_handler


class GroundTruthWriter(Writer):
    """
    Ground truth writer.
    
    Args:
        file_handler (io.IOBase): It can be file name or file handler.
    """
    def __init__(self, file_handler):
        self._file_handler = get_file_handler(file_handler)
        fieldnames = ['id1', 'id2', 'label']
        self._csv_writer = csv.DictWriter(self._file_handler, fieldnames=fieldnames)
        self._csv_writer.writeheader()

    def write(self, id1: str, id2: str, label: bool):
        """
        Writer to file.
        
        Args:
            id1 (str): Id 1.
            id2 (str): Id 2.
            label (bool): Positive (True) or negative (False).
        """
        self._csv_writer.writerow({'id1': id1, 'id2': id2, 'label': label})

    def close(self):
        try:
            self._file_handler.close()
        except:
            pass
