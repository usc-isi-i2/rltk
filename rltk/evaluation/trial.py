import heapq
import pandas as pd
import copy

from rltk.record import Record, get_property_names
from rltk.evaluation.ground_truth import GroundTruth
from scipy.optimize import linear_sum_assignment
from typing import Any


class Trial(object):
    """
    Trial stores the calculated result for further evaluation.
    It only saves the result which is also in ground truth.
    
    Args:
        ground_truth (GroundTruth): Ground truth.
        min_confidence (float): If the result has lower confidence than min confidence, it will not be saved.
                                Default is 0.
        top_k (int): Max number of result to be saved. 0 means no limitation.
                    Default is 0.
        **kwargs: Other user-defined properties.
    """

    class Result:
        """
        Result data structure

        Args:
            record1 (Record): first record
            record2 (Record): second record
            is_positive (bool): if the prediction of these two records is pair
            confidence (float): the probability of positive
        """

        def __init__(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None, **kwargs):
            self.record1 = record1
            self.record2 = record2
            self.is_positive = is_positive
            self.confidence = confidence
            self.extra_key_values = kwargs

        def __deepcopy__(self, memo):
            # Notice: record objects are NOT deep copied. Only reference is used here.
            cls = self.__class__
            copied = cls(record1=self.record1, record2=self.record2, is_positive=self.is_positive,
                         confidence=self.confidence)
            copied.extra_key_values = copy.deepcopy(self.extra_key_values)
            return copied

        def __cmp__(self, other):
            return self.confidence < other.confidence

        def __lt__(self, other):
            return self.confidence < other.confidence

        def __getattr__(self, key):
            return self.extra_key_values[key]

        def get_property_names(self):
            """
            Get all properties in Result
            
            Returns:
                list:
            """
            return ['is_positive', 'confidence'] + list(self.extra_key_values.keys())
            
    def __init__(self, ground_truth: GroundTruth, min_confidence: float = 0, top_k: int = 0, **kwargs):
        self._ground_truth = ground_truth
        self._min_confidence = min_confidence
        self._top_k = top_k
        self._results = []
        self.extra_key_values = kwargs
        self.pre_evaluate()

    def __deepcopy__(self, memo):
        """
        Deep copy of trial and trial results.
        
        Args:
            memo (dict): Argument `memo <https://docs.python.org/3.6/library/copy.html>`_ of :py:meth:`copy.deepcopy`.
            
        Note:
            `Record` in `Result` is still reference.
            
        Returns:
            Trial: Cloned object.
        """
        cls = self.__class__
        copied = cls(ground_truth=self._ground_truth, min_confidence=self._min_confidence, top_k=self._top_k)
        copied._results = copy.deepcopy(self._results)
        copied._extra_key_value = copy.deepcopy(self.extra_key_values)
        copied.tp = self.tp
        copied.tn = self.tn
        copied.fp = self.fp
        copied.fn = self.fn
        copied.tp_list = self.tp_list
        copied.tn_list = self.tn_list
        copied.fp_list = self.fp_list
        copied.fn_list = self.fn_list
        return copied

    def clone(self):
        """
        Same as :meth:`__deepcopy__`.
        """
        return copy.deepcopy(self)

    def add_property(self, key: str, value: Any):
        """
        Add new property to Trial
        
        Args:
            key (str): Key name
            value (Any): Any type of value
        """
        self.extra_key_values[key] = value

    def __getattr__(self, key):
        try:
            return self.extra_key_values[key]
        except:
            raise AttributeError

    def __iter__(self):
        """
        Same as :meth:`__next__`
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator
        
        Returns:
            iter: Result
        """
        for r in self._results:
            yield r

    def pre_evaluate(self):
        """
        Preparation before evaluation
        """
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.tp_list = []
        self.tn_list = []
        self.fp_list = []
        self.fn_list = []

    def evaluate(self, threshold: float = None):
        """
        Run evaluation
        
        Args:
            threshold (float, optional): Only if :meth:`Result.confidence` is greater than this threshold,
                                    `Result.is_positive` will be set to True. 
                                    If it's None, then `Result.is_positive` is used.
                                    Default is None.
                                    
        Note:
            If `threshold` is set:
            :meth:`Result.is_positive` will be overwritten.
            :meth:`Result.confidence` should be set.
        """
        self.pre_evaluate()

        for trial_result in self._results:
            if threshold is not None:
                trial_result.is_positive = False
                if trial_result.confidence >= threshold:
                    trial_result.is_positive = True

            gt_positive = self._ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
            trial_positive = trial_result.is_positive

            if trial_positive and gt_positive:
                self.tp_list.append(trial_result)
            elif not trial_positive and not gt_positive:
                self.tn_list.append(trial_result)
            elif trial_positive and not gt_positive:
                self.fp_list.append(trial_result)
            elif not trial_positive and gt_positive:
                self.fn_list.append(trial_result)

        self.tp = len(self.tp_list)
        self.tn = len(self.tn_list)
        self.fp = len(self.fp_list)
        self.fn = len(self.fn_list)

    def run_munkres(self, threshold=0):
        """
        Run Munkres algorithm (also called the Hungarian algorithm) on all pairs in Trial. 
        Only run this method if the linkage between two datasets are one to one.
        
        Args:
            threshold (float, optional): Only if :meth:`Result.confidence` is greater than this threshold,
                                    `Result.is_positive` will be set to True.
                                    Default is 0.
        
        Note:
            :meth:`Result.is_positive` will be overwritten.
            :meth:`Result.confidence` should be set.
        """
        r1ids = [r.record1.id for r in self._results]
        r2ids = [r.record2.id for r in self._results]
        confs = [r.confidence for r in self._results]
        r1_idx = {v: i for i, v in enumerate(set(r1ids))}  # id -> index
        r2_idx = {v: i for i, v in enumerate(set(r2ids))}  # id -> index
        matrix = [len(r2_idx) * [1] for _ in range(len(r1_idx))]
        for i in range(len(r1ids)):
            matrix[r1_idx[r1ids[i]]][r2_idx[r2ids[i]]] = 1.0 - confs[i]

        # TODO:
        # replace Munkres here by an implementation supports sparse matrix

        row_idx, col_idx = linear_sum_assignment(matrix)
        indexes = set([(r, c) for r, c in zip(row_idx, col_idx)])

        for trial_result in self._results:
            trial_result.is_positive = False
            if (r1_idx[trial_result.record1.id], r2_idx[trial_result.record2.id]) in indexes:
                if trial_result.confidence >= threshold:
                    trial_result.is_positive = True

    def add_result(self, record1: Record, record2: Record, is_positive: bool, confidence: float = 1, **kwargs) -> None:
        """
        Add comparison result

        Args:
            record1 (Record): first record.
            record2 (Record): second record.
            is_positive (bool): if the prediction of these two records is pair
            confidence (float): the probability of positive
        """
        if confidence >= self._min_confidence and self._ground_truth.is_member(record1.id, record2.id):
            if self._top_k == 0 or len(self._results) < self._top_k:
                cur = self.Result(record1, record2, is_positive, confidence, **kwargs)
                heapq.heappush(self._results, cur)
            elif confidence > self._results[0].confidence:
                heapq.heappop(self._results)
                cur = self.Result(record1, record2, is_positive, confidence, **kwargs)
                heapq.heappush(self._results, cur)

    def add_positive(self, *args, **kwargs):
        """
        Syntactic sugar of :meth:`add_result`
        """
        self.add_result(*args, is_positive=True, **kwargs)

    def add_negative(self, *args, **kwargs):
        """
        Syntactic sugar of :meth:`add_result`
        """
        self.add_result(*args, is_positive=False, **kwargs)

    def get_all_data(self):
        """
        Get all saved Result

        Returns:
            list[Result]:
        """
        return self._results

    def get_ground_truth(self):
        """
        Get associated GroundTruth

        Returns:
            GroundTruth:
        """
        return self._ground_truth

    @property
    def precision(self) -> float:
        """
        precision = true positive / (true positive + false positive)

        Returns:
            float:
        """
        if (self.tp + self.fp) == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        """
        recall = true positive / (true positive + false negative)

        Returns:
            float:
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def f_measure(self) -> float:
        """
        f_measure = 2 * precision * recall / (precision + recall)

        Returns:
            float:
        """
        return 2 * (self.precision * self.recall) / (self.precision + self.recall)
        
    @property
    def false_positives(self) -> float:
        """
        false positive ratio = false positive / (false positive + true negative)

        Returns:
            float:
        """
        if (self.fp + self.tn) == 0:
            return 0.0
        return self.fp / (self.fp + self.tn)

    @property
    def true_positives(self) -> float:
        """
        true positive ratio = true positive / (true positive + false negative)

        Returns:
            float:
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def false_negatives(self) -> float:
        """
        false negative ratio = false negative / (false negative + true positive)

        Returns:
            float:
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.fn / (self.tp + self.fn)

    @property
    def true_negatives(self) -> float:
        """
        true negative ratio = true negative / (true negative + false positive)

        Returns:
            float:
        """
        if (self.fp + self.tn) == 0:
            return 0.0
        return self.tn / (self.fp + self.tn)

    @property
    def false_discovery(self):
        """
        false discovery = false positive / (false positive + true positive)

        Returns:
            float:
        """
        if (self.fp + self.tp) == 0:
            return 0.0
        return self.fp / (self.fp + self.tp)

    @property
    def true_positives_list(self):
        """
        List of all true positives
        
        Returns:
            list:
        """
        return self.tp_list

    @property
    def true_negatives_list(self):
        """
        List of all true negatives
        
        Returns:
            list:
        """
        return self.tn_list

    @property
    def false_positives_list(self):
        """
        List of all false positives
        
        Returns:
            list:
        """
        return self.fp_list

    @property
    def false_negatives_list(self):
        """
        List of all false negatives
        
        Returns:
            list:
        """
        return self.fn_list

    def generate_dataframe(self, results, record1_columns=None, record2_columns=None, result_columns=None, **kwargs):
        """
        Generate Pandas Dataframe
        
        Args:
            results (list): Result list
            record1_columns (list, optional): List of property names from record 1 which need to be shown in dataframe columns.
                                            Default is None, all properties are used.
            record2_columns (list, optional): List of property names from record 2 which need to be shown in dataframe columns.
                                            Default is None, all properties are used.
            result_columns (list, optional): List of property names from result which need to be shown in dataframe columns.
                                            Default is None, all properties are used.
            **kwargs: Parameters of pandas.Dataframe.
            
        Returns:
            pandas.DataFrame:
        """

        table = []
        r1_columns = record1_columns
        r2_columns = record2_columns
        res_columns = result_columns

        # construct table
        for result in results:

            # generate columns based on first result
            if not r1_columns:
                r1_columns = get_property_names(result.record1.__class__)
            if not r2_columns:
                r2_columns = get_property_names(result.record2.__class__)
            if not res_columns:
                res_columns = result.get_property_names()

            # get data
            r1_data = []
            r2_data = []
            res_data = []
            gt_data = []
            for prop_name in r1_columns:
                r1_data.append(getattr(result.record1, prop_name))
            for prop_name in r2_columns:
                r2_data.append(getattr(result.record2, prop_name))
            for prop_name in res_columns:
                res_data.append(getattr(result, prop_name))
            gt_data.append(self._ground_truth.get_label(result.record1.id, result.record2.id))

            # append data
            table.append(r1_data + r2_data + gt_data + res_data)

        r1_columns = ['record1.{}'.format(p) for p in r1_columns]
        r2_columns = ['record2.{}'.format(p) for p in r2_columns]
        columns = r1_columns + r2_columns + ['ground_truth.label'] + res_columns
        return pd.DataFrame(table, columns=columns, **kwargs)
