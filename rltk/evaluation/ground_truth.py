import json
import heapq
import random
from typing import Callable
import pandas as pd
from collections import OrderedDict
from operator import itemgetter
import copy

from rltk.utils import get_record_pairs
from rltk.io.reader import GroundTruthReader
from rltk.io.writer import GroundTruthWriter

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rltk.dataset import Dataset


class GroundTruth(object):
    """
    Ground Truth
    
    Args:
        filename (string, optional): existing ground truth file name
        negative_if_not_exists (bool, optional): If pair is not in ground truth, it will be treated as negative pair
                                        (when you use :meth:`is_positive`, :meth:`is_negative`, :meth:`get_label`).
                                        Defaults to False.
    """
    ID1 = 'id1'
    ID2 = 'id2'
    LABEL = 'label'

    def __init__(self, filename: str = None, negative_if_not_exists: bool = False):
        self._ground_truth_data = {}
        self._gt_id1s = set([])
        self._gt_id2s = set([])
        self._negative_if_not_exists = negative_if_not_exists

        if filename:
            self.load(filename)

    def add_positive(self, id1: str, id2: str):
        """
        Add a positive ground truth. It's a syntactic sugar of :meth:`add_ground_truth`.

        Args:
            id1 (str): first id
            id2 (str): second id
        """
        self.add_ground_truth(id1, id2, True)

    def add_negative(self, id1: str, id2: str):
        """
        Add a negative ground truth. It's a syntactic sugar of :meth:`add_ground_truth`.

        Args:
            id1 (str): first id
            id2 (str): second id
        """
        self.add_ground_truth(id1, id2, False)

    def add_ground_truth(self, id1: str, id2: str, value: bool):
        """
        Add a pair to ground truth

        Args:
            id1 (str): first id
            id2 (str): second id
            value (bool): ground truth value
        """
        key = self.encode_ids(id1, id2)
        self._ground_truth_data[key] = value
        self._gt_id1s.add(id1)
        self._gt_id2s.add(id2)

    def is_member(self, id1: str, id2: str) -> bool:
        """
        Check if this pair is in ground truth

        Args:
            id1 (str): first id
            id2 (str): second id

        Returns:
            bool:

        Note:
            This method is not impacted by `negative_if_not_exists`.
        """
        key = self.encode_ids(id1, id2)
        return key in self._ground_truth_data

    def get_label(self, id1: str, id2: str) -> bool:
        """
        Pair's label
        
        Args:
            id1 (str): first id
            id2 (str): second id
        
        Returns:
            bool: True if positive, else negative

        Raises:
            KeyError: if pair is not in ground truth
        """
        if not self.is_member(id1, id2):
            if self._negative_if_not_exists:
                return False
            raise KeyError('Not in ground truth')
        key = self.encode_ids(id1, id2)
        return self._ground_truth_data.get(key)

    def is_positive(self, id1: str, id2: str) -> bool:
        """
        If pair is positive in ground truth. It's a syntactic sugar of :meth:`get_label`.

        Args:
            id1 (str): first id
            id2 (str): second id

        Returns:
            bool:
            
        Raises:
            KeyError: if pair is not in ground truth
        """
        return self.get_label(id1, id2)

    def is_negative(self, id1: str, id2: str) -> bool:
        """
        If pair is negative in ground truth. It's a syntactic sugar of :meth:`get_label`.

        Args:
            id1 (str): first id
            id2 (str): second id

        Returns:
            bool:
            
        Raises:
            KeyError: if pair is not in ground truth
        """
        return not self.get_label(id1, id2)

    def load(self, filename: str):
        """
        Load the ground truth from file

        Args:
            filename (str): loading path
        """
        for obj in GroundTruthReader(filename):
            self._ground_truth_data[self.encode_ids(obj[self.ID1], obj[self.ID2])] = obj[self.LABEL] == 'True'

    def save(self, filename: str):
        """
        Save the ground truth to file

        Args:
            filename (str): saving path
        """
        w = GroundTruthWriter(filename)
        for k, v in self._ground_truth_data.items():
            ids = json.loads(k)
            w.write(ids[self.ID1], ids[self.ID2], v)
        w.close()

    def encode_ids(self, id1: str, id2: str):
        """
        Encode ids to key in ground truth dictionary

        Args:
            id1 (str): first id
            id2 (str): second id

        Returns:
            string:
        """
        key = json.dumps({self.ID1: id1, self.ID2: id2})
        return key

    def decode_ids(self, key: str):
        """
        Decode key in ground truth dictionary to ids

        Args:
            key (str):

        Returns:
            tuple:
                id1 (str)
                id2 (str)
        """
        obj = json.loads(key)
        return obj[self.ID1], obj[self.ID2]

    def __iter__(self):
        """
        Same as :meth:`__next__`
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator
        
        Returns:
            iter: id1, id2, label
        """
        for k, v in self._ground_truth_data.items():
            id1, id2 = self.decode_ids(k)
            yield id1, id2, v

    def __len__(self):
        """
        Size of ground truth
        """
        return len(self._ground_truth_data)

    def generate_negatives(self, dataset1: 'Dataset', dataset2: 'Dataset',
                           score_function: Callable, num_of_negatives: int = -1,
                           range_in_gt: bool = False, exclude_from: 'GroundTruth' = None):
        """
        Args:
            dataset1 (Dataset): Dataset 1.
            dataset2 (Dataset): Dataset 2.
            score_function (Callable): User function, inputs are two :meth:`rltk.record.Record` s, return is a float.
            num_of_negatives (int, optional): Number of negatives to generate. 
                                            Default is -1 which will generate same number of negatives to positives.
            range_in_gt (bool, optional): The negatives will be generated within the range of ids 
                                        in ground truth if it's True,
                                        otherwise range will be the cross product of two datasets. 
                                        Default is False.
            exclude_from (GroundTruth, optional): Exclude the id pair which appears in this ground truth. 
                                            Defaults to None.
                                            This is especially useful when generating negatives for test set \
                                            meanwhile the pairs in train set need to be excluded.
        """
        num_of_negatives = len(self) if num_of_negatives == -1 else num_of_negatives
        max_heap = []

        for r1, r2 in get_record_pairs(dataset1, dataset2):
            if not self.is_member(r1.id, r2.id) and \
                    (not exclude_from or not exclude_from.is_member(r1.id, r2.id)) and \
                    (not range_in_gt or (r1.id in self._gt_id1s and r2.id in self._gt_id2s)):
                s = score_function(r1, r2)
                heapq.heappush(max_heap, (s, r1.id, r2.id))
                if len(max_heap) > num_of_negatives:
                    heapq.heappop(max_heap)

        for d in max_heap:
            r1_id, r2_id = d[1], d[2]
            self.add_negative(r1_id, r2_id)

    def generate_all_negatives(self, dataset1: 'Dataset', dataset2: 'Dataset',
                               range_in_gt: bool = False, exclude_from: 'GroundTruth' = None):
        """
        Args:
            dataset1 (Dataset): Dataset 1.
            dataset2 (Dataset): Dataset 2.
            range_in_gt (bool, optional): The negatives will be generated within the range of ids 
                                        in ground truth if it's True,
                                        otherwise range will be the cross product of two datasets. 
                                        Default is False.
            exclude_from (GroundTruth, optional): Exclude the id pair which appears in this ground truth. 
                                            Defaults to None.
                                            This is especially useful when generating negatives for test set \
                                            meanwhile the pairs in train set need to be excluded.
        """
        for r1, r2 in get_record_pairs(dataset1, dataset2):
            if not self.is_member(r1.id, r2.id) and \
                    (not exclude_from or not exclude_from.is_member(r1.id, r2.id)) and \
                    (not range_in_gt or (r1.id in self._gt_id1s and r2.id in self._gt_id2s)):
                self.add_negative(r1.id, r2.id)

    def generate_stratified_negatives(self, dataset1: 'Dataset', dataset2: 'Dataset',
                                      classify: Callable, num_of_strata: int, random_seed: int = None,
                                      num_of_negatives: int = -1,
                                      range_in_gt: bool = False, exclude_from: 'GroundTruth' = None):
        """
        Args:
            dataset1 (Dataset): Dataset 1.
            dataset2 (Dataset): Dataset 2.
            classify (Callable): User function, inputs are two :meth:`rltk.record.Record` s, 
                                return is an integer which identify which stratum the pair belongs to.
                                The return integer should be in range [0, num_of_strata).
            num_of_strata (int): Number of strata.
            random_seed (int, optional): The seed used by :py:meth:`random.seed`.
            num_of_negatives (int, optional): Number of negatives to generate. 
                                            Default is -1 which will generate same number of negatives to positives.
            range_in_gt (bool, optional): The negatives will be generated within the range of ids 
                                        in ground truth if it's True,
                                        otherwise range will be the cross product of two datasets. 
                                        Default is False.
            exclude_from (GroundTruth, optional): Exclude the id pair which appears in this ground truth. 
                                            Defaults to None.
                                            This is especially useful when generating negatives for test set \
                                            meanwhile the pairs in train set need to be excluded.
        """

        # add positives and negatives to different clusters
        strata = [{'p': [], 'n': []} for _ in range(num_of_strata)]

        # build strata
        for r1, r2 in get_record_pairs(dataset1, dataset2):
            if (range_in_gt and not (r1.id in self._gt_id1s and r2.id in self._gt_id2s)) or \
                    (exclude_from and exclude_from.is_member(r1.id, r2.id)):
                continue
            stratum_id = classify(r1, r2)
            p_n = 'p' if self.is_member(r1.id, r2.id) else 'n'
            strata[stratum_id][p_n].append((r1.id, r2.id))

        # compute weights: p / n
        strata_weights = {}
        for idx, s in enumerate(strata):
            stratum_id = str(idx)
            # nothing to pick
            if len(s['p']) == 0 or len(s['n']) == 0:
                strata_weights[stratum_id] = 0.0
                continue
            strata_weights[stratum_id] = float(len(s['p'])) / len(s['n'])

        # sorting
        sorted_strata_weights = OrderedDict(sorted(strata_weights.items(), key=itemgetter(1), reverse=True))

        # find out the number of negatives to pick from each stratum
        total_num = sum([len(s['p']) for s in strata]) if num_of_negatives == -1 else num_of_negatives
        num_to_pick_from_each_stratum = [0] * num_of_strata
        curr_strata_weights = copy.deepcopy(sorted_strata_weights)
        for stratum_id in sorted_strata_weights.keys():
            if total_num <= 0 or len(curr_strata_weights) == 0:
                break
            weight = sorted_strata_weights[stratum_id]
            idx = int(stratum_id)
            # normalize weights
            denominator = sum([w for w in curr_strata_weights.values()])
            num_to_pick_from_each_stratum[idx] = \
                min(round(total_num * weight / denominator), len(strata[idx]['n']))
            # prep for next round
            total_num -= num_to_pick_from_each_stratum[idx]
            curr_strata_weights.popitem(last=False)

        # pick negatives
        if random_seed:
            random.seed(random_seed)
        for idx, num in enumerate(num_to_pick_from_each_stratum):
            negs = random.sample(strata[idx]['n'], num)
            for n in negs:
                self.add_negative(n[0], n[1])

    def remove_negatives(self):
        """
        Remove all negatives from ground truth
        """
        keys_to_delete = []
        for key, label in self._ground_truth_data.items():
            if not label:
                keys_to_delete.append(key)
        for k in keys_to_delete:
            del self._ground_truth_data[k]

    def train_test_split(self, test_ratio: float = 0.3, random_seed: int = None):
        """
        Train test split.
        
        Args:
            test_ratio (float, optional): The ratio of test from all ground truth data. Default is 0.3.
            random_seed (int, optional): The seed used by :py:meth:`random.seed`.
        Returns:
            tuple:
                train_gt (GroudTruth)
                test_gt (GroudTruth)
        """
        if random_seed:
            random.seed(random_seed)

        train_gt, test_gt = GroundTruth(), GroundTruth()
        size = len(self)
        test_size = int(size * test_ratio)

        indices = [i for i in range(size)]
        random.shuffle(indices)
        test_indices = set(indices[:test_size])

        for idx, (id1, id2, label) in enumerate(self):
            if idx in test_indices:
                test_gt.add_ground_truth(id1, id2, label)
            else:
                train_gt.add_ground_truth(id1, id2, label)

        return train_gt, test_gt

    def generate_dataframe(self, **kwargs):
        """
        Generate data frame
        
        Returns:
            pandas.DataFrame:
        """
        columns = ['id1', 'id2', 'label']
        table = []
        for id1, id2, label in self:
            table.append([id1, id2, label])
        return pd.DataFrame(table, columns=columns, **kwargs)
