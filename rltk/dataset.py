from rltk.io.reader import Reader, BlockReader
from rltk.io.adapter import KeyValueAdapter, MemoryAdapter
from rltk.record import Record, generate_record_property_cache


class Dataset(object):
    def __init__(self, reader: Reader = None, record_class: Record = None, adapter: KeyValueAdapter = None):
        if not adapter:
            adapter = MemoryAdapter()
        self._adapter = adapter

        # build index
        if reader and record_class:
            self._reader = reader
            self._record_class = record_class

            self._build_index()

    def _build_index(self):
        if not self._reader or not self._record_class:
            raise ValueError('Reader or Record class is not provided.')
        for raw_object in self._reader:
            record_instance = self._record_class(raw_object)
            generate_record_property_cache(record_instance)
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
