import itertools

from rltk.io.reader import Reader
from rltk.blocking.block_dataset_id import BlockDatasetID
from rltk.io.adapter.key_set_adapter import KeySetAdapter


class BlockReader(Reader):
    """
    Block reader.
    
    Args:
        key_set_adapter (KeySetAdapter): Key set adapter.
    """

    def __init__(self, key_set_adapter: KeySetAdapter):
        super(BlockReader, self).__init__()
        self.key_set_adapter = key_set_adapter

    def __next__(self):
        """
        Iterator of id pairs generated according to blocks.
        
        Returns:
            iter: id1, id2.
        """
        for block_id, data in self.key_set_adapter:
            # fetch one block
            ds1, ds2 = list(), list()
            for dataset_id, record_id in data:
                if dataset_id == BlockDatasetID.Dataset1:
                    ds1.append(record_id)
                elif dataset_id == BlockDatasetID.Dataset2:
                    ds2.append(record_id)

            # cross product
            for id1, id2 in itertools.product(ds1, ds2):
                yield block_id, id1, id2
