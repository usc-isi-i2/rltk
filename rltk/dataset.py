from rltk.io.reader import Reader, BlockReader
from rltk.io.adapter import KeyValueAdapter, MemoryAdapter
from rltk.record import Record, generate_record_property_cache


class Dataset(object):
    """
    A set of records.
    
    Args:
        reader (Reader, optional): Input reader.
        record_class (type(Record), optional): Sub class of Record.
        adapter (KeyValueAdapter, optional): Specify where to store indexed data. Defaults to MemoryAdapter.
<<<<<<< HEAD
        
=======
        size (int, optional): Maximum size of records will be in Dataset, defaults to None, can be used when debugging.
>>>>>>> usc-isi-i2/v2
    Note:
        Set reader, record_class and adapter if new a Dataset needs to be generated.
        If Dataset is already generated and stored in a permanent adapter, only adapter needs to be provided.
    """
<<<<<<< HEAD
    def __init__(self, reader: Reader = None, record_class: type(Record) = None, adapter: KeyValueAdapter = None):
=======
    def __init__(self, reader: Reader = None, record_class: type(Record) = None, adapter: KeyValueAdapter = None,
                 size: int = None):
>>>>>>> usc-isi-i2/v2
        if not adapter:
            adapter = MemoryAdapter()
        self._adapter = adapter
        self._size = size

        # build index
        if reader and record_class:
            self._reader = reader
            self._record_class = record_class

            self._build_index()

    def _build_index(self):
        if not self._reader or not self._record_class:
            raise ValueError('Reader or Record class is not provided.')
        size = 0
        for raw_object in self._reader:
            record_instance = self._record_class(raw_object)
            generate_record_property_cache(record_instance)
            self._adapter.set(record_instance.id, record_instance)

            size += 1
            if self._size and size >= self._size:
                break

    def get_record(self, record_id):
        """
        Getter of a record.
        Args:
            record_id (str): Record id.
        Returns:
            Record: Record object.
        """
        return self._adapter.get(record_id)

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for r in self._adapter:
            yield r


def get_record_pairs(dataset1: Dataset, dataset2: Dataset, block_reader: BlockReader = None):
    """
    Generate pairs to compare.
    
    Args:
        dataset1 (Dataset): dataset 1
        dataset2 (Dataset): dataset 2
    """
    if not block_reader:
        for r1 in dataset1:
            for r2 in dataset2:
                yield r1, r2
    else:
        for id1, id2 in block_reader:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
