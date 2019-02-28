from rltk.io.reader import Reader
from rltk.io.adapter import KeyValueAdapter, MemoryKeyValueAdapter
from rltk.record import Record, generate_record_property_cache, get_property_names, get_cached_property_names
from rltk.parallel_processor import ParallelProcessor

import pandas as pd
from typing import Callable


class Dataset(object):
    """
    A set of records.
    
    Args:
        reader (Reader, optional): Input reader.
        record_class (type(Record), optional): Concrete class of :meth:`Record`.
        adapter (KeyValueAdapter, optional): Specify where to store indexed data. Defaults to :meth:`MemoryKeyValueAdapter`.
        size (int, optional): Same as `size` in :meth:`add_records` .
        pp_num_of_processor (int, optional): Same as `pp_num_of_processor` in :meth:`add_records` .
        pp_max_size_per_input_queue (int, optional): Same as `pp_max_size_per_input_queue` in :meth:`add_records` .
        sampling_function (callable, optional): Sampling function, `raw_object` is the only parameter. \
                                                If it returns True, record instance will be created.
    Note:
        - Set `reader`, `record_class` and `adapter` if new a :meth:`Dataset` needs to be generated.
        - If :meth:`Dataset` is already generated and stored in a permanent adapter, only adapter needs to be provided.
        - `reader` can also be added later, but `record_class` needs to be provided.
        
    """

    _METADATA_KEY = '__rltk_reserved_metadata'

    def __init__(self, reader: Reader = None, record_class: type(Record) = None, adapter: KeyValueAdapter = None,
                 size: int = None, sampling_function: Callable = None,
                 pp_num_of_processor: int = 0, pp_max_size_per_input_queue: int = 200):
        # load adapter and metadata if it's there
        self._adapter = adapter or MemoryKeyValueAdapter()
        metadata = self._adapter.get(self._METADATA_KEY)
        if metadata:
            self.id = metadata.get('id')
            self._record_class = metadata.get('record_class')

        # add / update
        self._sampling_function = sampling_function
        if record_class:
            if hasattr(self, '_record_class'):
                if self._record_class != record_class:
                    raise ValueError('Different record class already exists in current adapter')
            else:
                # add metadata
                self._record_class = record_class
                self.id = self._record_class.__name__
                metadata = {'id': self.id, 'record_class': self._record_class}
                self._adapter.set(self._METADATA_KEY, metadata)
            # add data
            if reader:
                self.add_records(reader, size, pp_num_of_processor, pp_max_size_per_input_queue)

    def add_records(self, reader: Reader, size: int = None,
                    pp_num_of_processor: int = 0, pp_max_size_per_input_queue: int = 200):
        """
        Add `records` to :meth:`Dataset` from `reader` .
        
        Args:
            reader (Reader, optional): Input reader.
            size (int, optional): Maximum size of records will be in :meth:`Dataset`, \
                            defaults to None, can be used when debugging.
            pp_num_of_processor (int, optional): Same as `num_of_processor` in :meth:`ParallelProcessor`. \ 
                            If non-zero is given and adapter is `parallel_safe`, \
                            this method will run in parallel mode. Defaults to 0.
            pp_max_size_per_input_queue (int, optional): Same as `max_size_per_input_queue` in \
                                    :meth:`ParallelProcessor`. Defaults to 200.
        """

        def generate(_raw_object):
            cached_property_names = get_cached_property_names(self._record_class)
            if not self._sampling_function or self._sampling_function(_raw_object):
                record_instance = self._record_class(_raw_object)
                generate_record_property_cache(record_instance, cached_property_names)
                self._adapter.set(record_instance.id, record_instance)

        if not self._record_class:
            raise ValueError('Record class is not provided.')
        curr_size = 0

        # serial
        if pp_num_of_processor == 0 or not self._adapter.parallel_safe:
            for raw_object in reader:
                if not self._sampling_function or self._sampling_function(raw_object):
                    generate(raw_object)
                    curr_size += 1
                    if size and curr_size >= size:
                        break
        # parallel
        else:
            pp = ParallelProcessor(input_handler=generate, num_of_processor=pp_num_of_processor,
                                   max_size_per_input_queue=pp_max_size_per_input_queue)
            pp.start()
            for raw_object in reader:
                if not self._sampling_function or self._sampling_function(raw_object):
                    pp.compute(raw_object)
                    curr_size += 1
                    if size and curr_size >= size:
                        break
            pp.task_done()
            pp.join()

    def set_record(self, record: Record):
        """
        Setter of a record.
        
        Args:
            record (Record): Record object.
        """
        return self._adapter.set(record.id, record)

    def get_record(self, record_id):
        """
        Getter of a record.
        
        Args:
            record_id (str): Record id.
            
        Returns:
            Record: Record object.
        """
        return self._adapter.get(record_id)

    def generate_dataframe(self, size: int = None, **kwargs):
        """
        Generate Pandas Dataframe
        
        Args:
            size (int, optional): How many records should be used to generate `pandas.Dataframe`. 
                                None means all. Defaults to None.
        
        Returns:
            pandas.Dataframe
        """
        table = []
        columns = None
        count = 0

        # construct table
        for r in self:
            if size and count >= size:
                break
            count += 1

            # generate columns based on first record
            if not columns:
                columns = get_property_names(r.__class__)

            # get data
            row_data = []
            for prop_name in columns:
                row_data.append(getattr(r, prop_name))

            # append data
            table.append(row_data)

        return pd.DataFrame(table, columns=columns, **kwargs)

    def head(self, n: int = 10):
        """
        Iterate on first n records.

        Args:
            n (int, optional): Number of records. Default to 10.

        Returns:
            iter: Record
        """
        for idx, r in enumerate(self.__next__()):
            if idx >= n:
                break
            yield r

    def filter(self, condition: Callable, n: int = 10):
        """
        Iterate on filtered n records.

        Args:
            condition (Callable): `function(r: Record) -> bool`. If the return is True, record will be selected.
            n (int, optional): Number of records. Default to 10.

        Returns:
            iter: Record
        """
        counter = 0
        for r in self.__next__():
            if counter >= n:
                break
            if condition(r):
                counter += 1
                yield r

    def __iter__(self):
        """
        Same as :meth:`__next__`
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator
        
        Returns:
            iter: Record
        """
        for k, v in self._adapter:
            if k == self._METADATA_KEY:
                continue
            yield v
