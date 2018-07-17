import json
import heapq
import pandas as pd

from rltk.record import Record, get_property_names
from rltk.evaluation.ground_truth import GroundTruth


class Trial(object):
    """
    Trial stores the calculate result.
    It will only save the result which is also in groud_truth, and then can be used to evaluate.
    By setting min_confidence, it can filter and save the result with a min confidence.
    By setting top_k, it will save at most k result order by confidence DESC.
    """

    class Result:
        """
        Result structure.
        Contain the 2 compared records, the is_positive result and confidence.

        Attributes:
            record1 (Record): first record
            record2 (Record): second record
            is_positive (bool): the result. true means 2 record are same, false means they are different
            confidence (float): how much confidence the similarity function has on the result
        """

        def __init__(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None, **kwargs):
            """
            init all information.
            Attributes:
                record1 (Record): first record
                record2 (Record): second record
                is_positive (bool): the result. true means 2 record are same, false means they are different
                confidence (float): how much confidence the similarity function has on the result
            """
            self.record1 = record1
            self.record2 = record2
            self.is_positive = is_positive
            self.confidence = confidence
            self.extra_key_values = kwargs

        def __cmp__(self, other):
            return self.confidence < other.confidence

        def __lt__(self, other):
            return self.confidence < other.confidence

        def __getattr__(self, key):
            return self.extra_key_values[key]

        def get_property_names(self):
            return ['is_positive', 'confidence'] + list(self.extra_key_values.keys())
            
    def __init__(self, ground_truth: GroundTruth, label: str = '', min_confidence: float = 0,
                 top_k: int = 0, **kwargs):
        """
        init data.

        Attributes:
            ground_truth (GroundTruth): whether to save the record data.
            min_confidence (float): if the result has lower confidence than min confidence, it will not be saved.
            top_k (int): the max number of result to be saved.
            key_1 (String): the attribute in first record be compared.
            key_2 (String): the attribute in second record be compared.
        """
        self._ground_truth = ground_truth
        self._min_confidence = min_confidence
        self.label = label
        self._top_k = top_k
        self._results = []
        self.extra_key_values = kwargs

    def add_property(self, key, value):
        self.extra_key_values[key] = value

    def __getattr__(self, key):
        try:
            return self.extra_key_values[key]
        except:
            raise AttributeError

    def pre_evaluate(self):
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0
        self.tp_list = []
        self.tn_list = []
        self.fp_list = []
        self.fn_list = []

    def evaluate(self):
        self.pre_evaluate()

        for trial_result in self._results:
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

    def add_result(self, record1: Record, record2: Record, is_positive: bool, confidence: float = 1, **kwargs) -> None:
        """
        Add one pair record comparison result.
        If confidence is less than min_confidence, it will skip.
        If confidence is less than the least confidence saved item and there are top_k items, it will skip.
        If confidence is more than the least confidence saved item and there are top_k items, the least confidence saved item will be removed and then save the current one.
        If it is not full, it wll directly save the current one.

        Attributes:
            record1 (Record): first record.
            record2 (Record): second record.
            is_positive (bool): the result of similarity function.
            confidence (float): how much confidence the similarity function has on the result.
        """
        if confidence >= self._min_confidence and self._ground_truth.is_member(record1.id, record2.id):
            if self._top_k == 0 or len(self._results) < self._top_k:
                cur = self.Result(record1, record2, is_positive, confidence, **kwargs)
                heapq.heappush(self._results, cur)
            elif confidence > self._results[0].confidence:
                heapq.heappop(self._results)
                cur = self.Result(record1, record2, is_positive, confidence, **kwargs)
                heapq.heappush(self._results, cur)

    def add_positive(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=True, **kwargs)

    def add_negative(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=False, **kwargs)

    def get_all_data(self):
        """
        get all saved data

        Returns:
            data (list)
        """
        return self._results

    def get_ground_truth(self):
        """
        get saved ground truth

        Returns:
            ground_truth (GroundTruth)
        """
        return self._ground_truth

    @property
    def precision(self) -> float:
        """
        Based on the mathematical formula:
            precision = true positive / (true positive + false positive)
        Calculate and return the precision

        Returns:
            precision (float)
        """
        if (self.tp + self.fp) == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        """
        return the true positive ratio

        Returns:
            recall (float)
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def f_measure(self) -> float:
        """
        Based on the mathematical formula:
            f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
        Calculate and return the f_measure

        Returns:
            f_measure (float)
        """
        return 1 / 2 * (self.precision + self.recall)

    @property
    def false_positives(self) -> float:
        """
        Based on the mathematical formula:
            false positive ratio = false positive / (false positive + true negative)
        Calculate and return the false positive ratio

        Returns:
            false positive ratio (float)
        """
        if (self.fp + self.tn) == 0:
            return 0.0
        return self.fp / (self.fp + self.tn)

    @property
    def true_positives(self) -> float:
        """
        Based on the mathematical formula:
            true positive ratio = true positive / (true positive + false negative)
        Calculate and return the true positive ratio

        Returns:
            true positive ratio (float)
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def false_negatives(self) -> float:
        """
        Based on the mathematical formula:
            false negative ratio = false negative / (false negative + true positive)
        Calculate and return the false negative ratio

        Returns:
            false negative ratio (float)
        """
        if (self.tp + self.fn) == 0:
            return 0.0
        return self.fn / (self.tp + self.fn)

    @property
    def true_negatives(self) -> float:
        """
        Based on the mathematical formula:
            true negative ratio = true negative / (true negative + false positive)
        Calculate and return the true negative ratio

        Returns:
            true negative ratio (float)
        """
        if (self.fp + self.tn) == 0:
            return 0.0
        return self.tn / (self.fp + self.tn)

    @property
    def false_discovery(self):
        """
        Based on the mathematical formula:
            false discovery = false positive / (false positive + true positive)
        Calculate and return the false false discovery

        Returns:
            false discovery (float)
        """
        if (self.fp + self.tp) == 0:
            return 0.0
        return self.fp / (self.fp + self.tp)

    @property
    def true_positives_list(self):
        return self.tp_list

    @property
    def true_negatives_list(self):
        return self.tn_list

    @property
    def false_positives_list(self):
        return self.fp_list

    @property
    def false_negatives_list(self):
        return self.fn_list

    def generate_dataframe(self, results, record1_columns=None, record2_columns=None, result_columns=None, **kwargs):

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
