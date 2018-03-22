from rltk.io.reader import Reader, BlockReader
from rltk.io.adapter import Adapter, MemoryAdapter
from rltk.record import Record


class Dataset(object):
    def __init__(self, reader: Reader, record_class: Record, adapter: Adapter = MemoryAdapter()):
        # build index
        if reader and record_class and adapter:
            self._reader = reader
            self._record_class = record_class
            self._adapter = adapter

            self._build_index()
        # load from adapter
        elif adapter:
            pass
        # error
        else:
            raise ValueError('Adapter is not specified.')

    def _build_index(self):
        if not self._reader or not self._record_class:
            raise ValueError('Reader or Record class is not provided.')
        for raw_object in self._reader:
            record_instance = self._record_class(raw_object)
            if not isinstance(record_instance.id, str):
                raise ValueError('Id in record should be in string (utf-8 encoded) type.')
            self._adapter.set(record_instance.id, record_instance)

    def get_record(self, record_id):
        return self._adapter.get(record_id)

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for r in self._adapter:
            yield r


def get_record_pairs(dataset1: Dataset, dataset2: Dataset, block_reader: BlockReader = None):
    if not block_reader:
        for r1 in dataset1:
            for r2 in dataset2:
                yield r1, r2
    else:
        for id1, id2 in block_reader:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
