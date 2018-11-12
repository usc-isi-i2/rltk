import itertools

from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.adapter.memory_key_set_adapter import MemoryKeySetAdapter
from rltk.dataset import Dataset
from rltk.record import Record


class Block(object):
    """
    Block
    
    key_set_adapter (keySetAdapter, optional): Where the block stores. If it's None, 
                                            :meth:`MemoryKeySetAdapter` is used. Defaults to None.
    """
    def __init__(self, key_set_adapter: KeySetAdapter = None):
        if not key_set_adapter:
            key_set_adapter = MemoryKeySetAdapter()
        self.key_set_adapter = key_set_adapter

    def add(self, block_id, dataset_id, record_id):
        """
        Add to block.
        
        Args:
            block_id (str): Block id.
            dataset_id (str / Dataset): Dataset id or Dataset object.
            record_id (str / Record): Record id or Record object.
        """
        if isinstance(dataset_id, Dataset):
            dataset_id = dataset_id.id
        if isinstance(record_id, Record):
            record_id = record_id.id
        self.key_set_adapter.add(block_id, (dataset_id, record_id))

    def get(self, block_id):
        """
        Get block by block_id.
        
        Args:
            block_id (str): Block id.
        
        Returns:
            set: {(dataset_id, record_id)}
        """
        return self.key_set_adapter.get(block_id)

    def __iter__(self):
        """
        Same as :meth:`__next__`
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator of blocks.

        Returns:
            iter: block_id, dataset_id, record_id.
        """
        for block_id, data in self.key_set_adapter:
            for dataset_id, record_id in data:
                yield block_id, dataset_id, record_id

    def pairwise(self, ds_id1: str, ds_id2: str = None):
        """
        Iterator of id pairs generated according to blocks.

        Returns:
            iter: block_id, id1, id2.
        """
        if isinstance(ds_id1, Dataset):
            ds_id1 = ds_id1.id
        if ds_id2 and isinstance(ds_id2, Dataset):
            ds_id2 = ds_id2.id

        if ds_id2:
            for block_id, data in self.key_set_adapter:
                # fetch one block
                ds1, ds2 = list(), list()
                for dataset_id, record_id in data:
                    if dataset_id == ds_id1:
                        ds1.append(record_id)
                    elif dataset_id == ds_id2:
                        ds2.append(record_id)

                # cross product
                for id1, id2 in itertools.product(ds1, ds2):
                    yield block_id, id1, id2
        else:
            for block_id, data in self.key_set_adapter:
                # fetch one block
                ds1 = list()
                for dataset_id, record_id in data:
                    if dataset_id == ds_id1:
                        ds1.append(record_id)

                # combinations of two elements
                for ds1, ds1_ in itertools.combinations(ds1, 2):
                    yield ds1, ds1_
