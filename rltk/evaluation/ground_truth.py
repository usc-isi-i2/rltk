import json
import heapq
import random
from typing import Callable

from rltk.utils import get_record_pairs
from rltk.io.reader import GroundTruthReader
from rltk.io.writer import GroundTruthWriter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rltk.dataset import Dataset


class GroundTruth(object):
    """
    ground truth container.
    A dict containing all ground truth
    the key is the combination of 2 id
    the value is the whether it is same by ground truth
    """
    ID1 = 'id1'
    ID2 = 'id2'
    LABEL = 'label'

    def __init__(self):
        self._ground_truth_data = {}

    def add_positive(self, id1: str, id2: str):
        """
        add a positive ground truth

        Attributes:
            id1 (String): first id
            id2 (String): second id
        """
        self.add_ground_truth(id1, id2, True)

    def add_negative(self, id1: str, id2: str):
        """
        add a negative ground truth

        Attributes:
            id1 (String): first id
            id2 (String): second id
        """
        self.add_ground_truth(id1, id2, False)

    def add_ground_truth(self, id1: str, id2: str, value: bool):
        """
        add a ground truth

        Attributes:
            id1 (String): first id
            id2 (String): second id
            value (bool): ground truth value
        """
        key = self.encode_ids(id1, id2)
        self._ground_truth_data[key] = value

    def is_member(self, id1: str, id2: str) -> bool:
        """
        check whether this item is in the ground truth dict

        Attributes:
            id1 (String): first id
            id2 (String): second id

        Returns:
            is_member (bool)
        """
        key = self.encode_ids(id1, id2)
        return key in self._ground_truth_data

    def get_label(self, id1: str, id2: str) -> bool:
        key = self.encode_ids(id1, id2)
        return self._ground_truth_data.get(key)

    def is_positive(self, id1: str, id2: str) -> bool:
        """
        if ground truth does not contain the item, raise a exception
        if ground truth contain the true value, return true; else, return false

        Attributes:
            id1 (String): first id
            id2 (String): second id

        Returns:
            is_positive (bool)
        """
        if not self.is_member(id1, id2):
            raise KeyError('Not in ground truth')
        return self.get_label(id1, id2)

    def is_negative(self, id1: str, id2: str) -> bool:
        """
        if ground truth does not contain the item, raise a exception
        if ground truth contain the true value, return false; else, return true

        Attributes:
            id1 (String): first id
            id2 (String): second id

        Returns:
            is_positive (bool)
        """
        if not self.is_member(id1, id2):
            raise KeyError('Not in ground truth')
        return not self.get_label(id1, id2)

    def load(self, filename):
        """
        load the ground truth from file.
        this will overwrite the current self.ground_trurh

        Attributes:
            filename (String): loading path
        """
        self.__init__()
        for obj in GroundTruthReader(filename):
            self._ground_truth_data[self.encode_ids(obj[self.ID1], obj[self.ID2])] = obj[self.LABEL] == 'True'

    def save(self, filename):
        """
        save the ground truth to file.

        Attributes:
            filename (String): saving path
        """
        w = GroundTruthWriter(filename)
        for k, v in self._ground_truth_data.items():
            ids = json.loads(k)
            w.write(ids[self.ID1], ids[self.ID2], v)
        w.close()

    def encode_ids(self, id1: str, id2: str):
        """
        combine id1 and id2 and gen the key to save in dict.

        Attributes:
            id1 (String): first id
            id2 (String): second id

        Returns:
            key (String)
        """
        key = json.dumps({self.ID1: id1, self.ID2: id2})
        return key

    def decode_ids(self, key: str):
        obj = json.loads(key)
        return obj[self.ID1], obj[self.ID2]

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        for k, v in self._ground_truth_data.items():
            id1, id2 = self.decode_ids(k)
            yield id1, id2, v

    def __len__(self):
        return len(self._ground_truth_data)

    def generate_negatives(self, dataset1: 'Dataset', dataset2: 'Dataset', score_function: Callable):
        size = len(self) # same size as positives
        max_heap = []

        for r1, r2 in get_record_pairs(dataset1, dataset2):
            if not self.is_member(r1.id, r2.id):
                s = score_function(r1, r2)
                heapq.heappush(max_heap, (s, r1.id, r2.id))
                if len(max_heap) > size:
                    heapq.heappop(max_heap)

        for d in max_heap:
            r1_id, r2_id = d[1], d[2]
            self.add_negative(r1_id, r2_id)

    def train_test_split(self, test_ratio: float = 0.2, random_seed: int = None):
        size = len(self)
        test_size = int(size * test_ratio)
        if random_seed:
            random.seed(random_seed)

        indices = [i for i in range(size)]
        random.shuffle(indices)
        test_indices = set(indices[:test_size])

        train_gt, test_gt = GroundTruth(), GroundTruth()
        for idx, (id1, id2, label) in enumerate(self):
            if idx in test_indices:
                test_gt.add_ground_truth(id1, id2, label)
            else:
                train_gt.add_ground_truth(id1, id2, label)

        return train_gt, test_gt