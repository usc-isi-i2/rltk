import json
import heapq

from rltk.record import Record
from rltk.evaluation.ground_truth import GroundTruth


class Trial(object):
    """
    Trial stores the calculate result.
    It will only save the result which is also in groud_truth, and then can be used to evaluate.
    By setting min_confidence, it can filter and save the result with a min confidence.
    By setting top_k, it will save at most k result order by confidence DESC.

    If save_record is true, it will save the record of all data.
    It is useful to check whether the similarity function is good, but will cost memory to store the data.

    Attributes:
        groud_truth (GroundTruth): whether to save the record data.
        min_confidence (float): if the result has lower confidence than min confidence, it will not be saved. min_confidence = 0 means all result will be saved.
        top_k (int): the max number of result to be saved. top_k = 0 means all result will be saved.
        save_record (bool): whether to save the record data.
    """

    class Result:
        """
        Result structure.
        Contain the 2 compared records, the is_positive result and confidence.
        if save_record is True, the whole item (including record information and confidence) will be stored.

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

    class Evaluator:
        """
        Evaluation compares the result of the trial and the ground truth (stored in trial),
        count and store the number of true positive, true negative, false positive, false negative.

        It can then provide the statistics of:
            true positive, true negative, false positive, false negative, f_measure, precision, false_discovery

        If save_record is true, it will save the record of all data in the provided trial besides the number of result

        Attributes:
            save_record (boolean): whether to save the record data
            tp (int): number of true positive
            tn (int): number of true negative
            fp (int): number of false positive
            fn (int): number of false negative
            tp_list (list, optional): saved true positive list
            tn_list (list, optional): saved true negative list
            fp_list (list, optional): saved false positive list
            fn_list (list, optional): saved false negative list
        """

        def __init__(self, save_record=False):
            """
            init the number of true positive, true negative, false positive, false negative to 0
            init save_record, default is False
            if save_record is True, init the true positive list, true negative list,
            false positive list, false negative list to empty list

            Args:
                save_record (boolean): Whether save the record of data. Defaults to False.
            """
            self.save_record = save_record
            self._reset()

        def _reset(self):

            self.tp = 0
            self.tn = 0
            self.fp = 0
            self.fn = 0

            self.tp_list = []
            self.tn_list = []
            self.fp_list = []
            self.fn_list = []

        def evaluate(self, ground_truth: GroundTruth, data: list):
            self._reset()

            for trial_result in data:
                gt_positive = ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
                trial_positive = trial_result.is_positive

                if trial_positive and gt_positive:
                    self.tp += 1
                    if self.save_record:
                        self.tp_list.append(trial_result)
                elif not trial_positive and not gt_positive:
                    self.tn += 1
                    if self.save_record:
                        self.tn_list.append(trial_result)
                elif trial_positive and not gt_positive:
                    self.fp += 1
                    if self.save_record:
                        self.fp_list.append(trial_result)
                elif not trial_positive and gt_positive:
                    self.fn += 1
                    if self.save_record:
                        self.fn_list.append(trial_result)

        def precision(self) -> float:
            """
            Based on the mathematical formula:
                precision = true positive / (true positive + false positive)
            Calculate and return the precision

            Returns:
                precision (float)
            """
            if self.tp + self.fp == 0:
                return 0.0
            return self.tp / (self.tp + self.fp)

        def recall(self) -> float:
            """
            return the true positive ratio

            Returns:
                recall (float)
            """
            return self.true_positives()

        def f_measure(self) -> float:
            """
            Based on the mathematical formula:
                f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
            Calculate and return the f_measure

            Returns:
                f_measure (float)
            """
            base = 2 * self.tp + self.fp + self.fn
            if base == 0:
                return 0.0
            return 2 * self.tp / base

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
            
    def __init__(self, ground_truth: GroundTruth, label: str = '', min_confidence: float = 0,
                 top_k: int = 0, save_record: bool = False):
        """
        init data.

        Attributes:
            ground_truth (GroundTruth): whether to save the record data.
            min_confidence (float): if the result has lower confidence than min confidence, it will not be saved.
            top_k (int): the max number of result to be saved.
            save_record (bool): whether to save the record data.
            key_1 (String): the attribute in first record be compared.
            key_2 (String): the attribute in second record be compared.
        """
        self._ground_truth = ground_truth
        self._min_confidence = min_confidence
        self.label = label
        self._top_k = top_k

        self._results = []
        self.save_record = save_record
        self.evaluator = None

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

    def evaluate(self):
        self.evaluator = self.Evaluator(self.save_record)
        self.evaluator.evaluate(self._ground_truth, self._results)

    @property
    def precision(self) -> float:
        """
        Based on the mathematical formula:
            precision = true positive / (true positive + false positive)
        Calculate and return the precision

        Returns:
            precision (float)
        """
        self.check_evaluator_init()
        return self.evaluator.precision()

    @property
    def recall(self) -> float:
        """
        return the true positive ratio

        Returns:
            recall (float)
        """
        self.check_evaluator_init()
        return self.evaluator.recall()

    @property
    def f_measure(self) -> float:
        """
        Based on the mathematical formula:
            f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
        Calculate and return the f_measure

        Returns:
            f_measure (float)
        """
        self.check_evaluator_init()
        return self.evaluator.f_measure()

    @property
    def false_positives(self) -> float:
        """
        Based on the mathematical formula:
            false positive ratio = false positive / (false positive + true negative)
        Calculate and return the false positive ratio

        Returns:
            false positive ratio (float)
        """
        self.check_evaluator_init()
        return self.evaluator.false_positives()

    @property
    def true_positives(self) -> float:
        """
        Based on the mathematical formula:
            true positive ratio = true positive / (true positive + false negative)
        Calculate and return the true positive ratio

        Returns:
            true positive ratio (float)
        """
        self.check_evaluator_init()
        return self.evaluator.true_positives()

    @property
    def false_negatives(self) -> float:
        """
        Based on the mathematical formula:
            false negative ratio = false negative / (false negative + true positive)
        Calculate and return the false negative ratio

        Returns:
            false negative ratio (float)
        """
        self.check_evaluator_init()
        return self.evaluator.false_negatives()

    @property
    def true_negatives(self) -> float:
        """
        Based on the mathematical formula:
            true negative ratio = true negative / (true negative + false positive)
        Calculate and return the true negative ratio

        Returns:
            true negative ratio (float)
        """
        self.check_evaluator_init()
        return self.evaluator.true_negatives()

    @property
    def false_discovery(self):
        """
        Based on the mathematical formula:
            false discovery = false positive / (false positive + true positive)
        Calculate and return the false false discovery

        Returns:
            false discovery (float)
        """
        self.check_evaluator_init()
        return self.evaluator.false_discovery()

    def check_evaluator_init(self):
        if not self.evaluator:
            raise Exception("Please run evaluator first")

    @property
    def true_positives_list(self):
        self.check_evaluator_init()
        return self.evaluator.tp_list

    @property
    def true_negatives_list(self):
        self.check_evaluator_init()
        return self.evaluator.tn_list

    @property
    def false_positives_list(self):
        self.check_evaluator_init()
        return self.evaluator.fp_list

    @property
    def false_negatives_list(self):
        self.check_evaluator_init()
        return self.evaluator.fn_list
