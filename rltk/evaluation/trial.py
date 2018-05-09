import json
import heapq

from rltk.record import Record, cached_property
from rltk.evaluation.ground_truth import GroundTruth


class Trial(object):
    '''
    Trial stores the calculate result.
    It will only save the result which is also in groud_truth, and then can be used to evaluate.
    By setting min_confidence, it can filter and save the result with a min confidence.
    By setting top_k, it will save at most k result order by confidence DESC.

    If save_rocord is true, it will save the record of all data.
    It is useful to check whether the similarity function is good, but will cost memory to store the data.

    Attributes:
        groud_truth (GroundTruth): whether to save the record data.
        min_confidence (float): if the result has lower confidence than min confidence, it will not be saved. min_confidence = 0 means all result will be saved.
        top_k (int): the max number of result to be saved. top_k = 0 means all result will be saved.
        save_record (bool): whether to save the record data.
        key_1 (String): the attribute in first record be compared.
        key_2 (String): the attribute in second record be compared.
    '''

    class TrialResult:
        '''
        Result structure.
        Contain the 2 compared record, the is_positive result and confidence.
        if save_record is True, the whole item (including record information and confidence) will be stored.

        Attributes:
            record1 (Record): first record
            record2 (Record): second record
            is_positive (bool): the result. true means 2 record are same, false means they are different
            confidence (float): how much confidence the similarity function has on the result
            save_record (bool): whether to save the record data
            key_1 (String): the attribute in first record be compared
            key_2 (String): the attribute in second record be compared
        '''

        def __init__(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None,
                     save_record: bool = False, key_1: str = None, key_2: str = None):
            '''
            init all information.
            Attributes:
                record1 (Record): first record
                record2 (Record): second record
                is_positive (bool): the result. true means 2 record are same, false means they are different
                confidence (float): how much confidence the similarity function has on the result
                save_record (bool): whether to save the record data
                key_1 (String): the attribute in first record be compared
                key_2 (String): the attribute in second record be compared
            '''
            self.record1 = record1
            self.record2 = record2
            self.is_positive = is_positive
            self.confidence = confidence

            if save_record:
                self.full_data = getattr(record1, key_1) + "; " + getattr(record2, key_2) + ": " + str(confidence)
            else:
                self.full_data = None

        def __cmp__(self, other):
            return self.confidence < other.confidence

        def __lt__(self, other):
            return self.confidence < other.confidence

    class SelfEvaluation:
        '''
        Evaluation compares the result of the trial and the ground truth (stored in trial),
        count and store the number of true positive, true negative, false positive, false negative.

        It can then provide the statistics of:
            true positive, true negative, false positive, false negative, f_measure, precision, false_discovery

        If save_rocord is true, it will save the record of all data in the provided trial besides the number of result

        Attributes:
            save_rocord (boolean): whether to save the record data
            tp (int): number of true positive
            tn (int): number of true negative
            fp (int): number of false positive
            fn (int): number of false negative
            tp_list (list, optional): saved true positive list
            tn_list (list, optional): saved true negative list
            fp_list (list, optional): saved false positive list
            fn_list (list, optional): saved false negative list
        '''

        def __init__(self, save_rocord=False):
            '''
            init the number of true positive, true negative, false positive, false negative to 0
            init save_rocord, default is False
            if save_rocord is True, init the true positive list, true negative list,
            false positive list, false negative list to empty list

            Args:
                save_rocord (boolean): Whether save the record of data. Defaults to False.
            '''
            self.tp = 0
            self.tn = 0
            self.fp = 0
            self.fn = 0
            self.save_rocord = save_rocord
            if (self.save_rocord):
                self.tp_list = []
                self.tn_list = []
                self.fp_list = []
                self.fn_list = []

        def evaluate(self, ground_truth: GroundTruth, data: list):
            '''
            Based on the trial and the ground truth (stored in trial), do statistics analysis.
            Save the statistics to the Class Args.

            Args:
                trial (Trial): the Trial to be analysis
            '''
            self.tp, self.tn, self.fp, self.fn, self.tp_list, self.tn_list, self.fp_list, self.fn_list = self.__statistics_trial(
                ground_truth, data)

        def precision(self) -> float:
            '''
            Based on the mathematical formula:
                precision = true positive / (true positive + false positive)
            Calculate and return the precision

            Returns:
                precision (float)
            '''
            if self.tp + self.fp == 0:
                return 0.0
            return self.tp / (self.tp + self.fp)

        def recall(self) -> float:
            '''
            return the true positive ratio

            Returns:
                recall (float)
            '''
            return self.true_positives()

        def f_measure(self) -> float:
            '''
            Based on the mathematical formula:
                f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
            Calculate and return the f_measure

            Returns:
                f_measure (float)
            '''
            base = 2 * self.tp + self.fp + self.fn
            if base == 0:
                return 0.0
            return 2 * self.tp / base

        def false_positives(self) -> float:
            '''
            Based on the mathematical formula:
                false positive ratio = false positive / (false positive + true negative)
            Calculate and return the false positive ratio

            Returns:
                false positive ratio (float)
            '''
            if (self.fp + self.tn) == 0:
                return 0.0
            return self.fp / (self.fp + self.tn)

        def true_positives(self) -> float:
            '''
            Based on the mathematical formula:
                true positive ratio = true positive / (true positive + false negative)
            Calculate and return the true positive ratio

            Returns:
                true positive ratio (float)
            '''
            if (self.tp + self.fn) == 0:
                return 0.0
            return self.tp / (self.tp + self.fn)

        def false_negatives(self) -> float:
            '''
            Based on the mathematical formula:
                false negative ratio = false negative / (false negative + true positive)
            Calculate and return the false negative ratio

            Returns:
                false negative ratio (float)
            '''
            if (self.tp + self.fn) == 0:
                return 0.0
            return self.fn / (self.tp + self.fn)

        def true_negatives(self) -> float:
            '''
            Based on the mathematical formula:
                true negative ratio = true negative / (true negative + false positive)
            Calculate and return the true negative ratio

            Returns:
                true negative ratio (float)
            '''
            if (self.fp + self.tn) == 0:
                return 0.0
            return self.tn / (self.fp + self.tn)

        def false_discovery(self):
            '''
            Based on the mathematical formula:
                false discovery = false positive / (false positive + true positive)
            Calculate and return the false false discovery

            Returns:
                false discovery (float)
            '''
            if (self.fp + self.tp) == 0:
                return 0.0
            return self.fp / (self.fp + self.tp)

        def __statistics_trial(self, ground_truth: GroundTruth, data: list):
            '''
            Analysis the calculate result in trial and filter them by ground truth.
            If save_rocord is False, only the number will be saved.
            If save_rocord is True, the record items will be saved, too.

            Args:
                trial (Trial): the Trial to be analysis

            Returns:
                tp (int): number of true positive
                tn (int): number of true negative
                fp (int): number of false positive
                fn (int): number of false negative
                tp_list (list, optional): saved true positive list
                tn_list (list, optional): saved true negative list
                fp_list (list, optional): saved false positive list
                fn_list (list, optional): saved false negative list
            '''
            if self.save_rocord:
                tp_list = []
                tn_list = []
                fp_list = []
                fn_list = []

                for trial_result in data:
                    gt_val = ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
                    cal_val = trial_result.is_positive

                    if cal_val and gt_val:
                        tp_list.append(trial_result.full_data)
                    elif not cal_val and not gt_val:
                        tn_list.append(trial_result.full_data)
                    elif cal_val and not gt_val:
                        fp_list.append(trial_result.full_data)
                    elif not cal_val and gt_val:
                        fn_list.append(trial_result.full_data)

                return len(tp_list), len(tn_list), len(fp_list), len(fn_list), tp_list, tn_list, fp_list, fn_list
            else:
                tp = 0
                tn = 0
                fp = 0
                fn = 0

                for trial_result in data:
                    gt_val = ground_truth.is_positive(trial_result.record1.id, trial_result.record2.id)
                    cal_val = trial_result.is_positive

                    if cal_val and gt_val:
                        tp += 1
                    elif not cal_val and not gt_val:
                        tn += 1
                    elif cal_val and not gt_val:
                        fp += 1
                    elif not cal_val and gt_val:
                        fn += 1

                return tp, tn, fp, fn, [], [], [], []
        # def get_true_positive_list(self):

    def __init__(self, groud_truth: GroundTruth, label: str = '', min_confidence: float = 0,
                 top_k: int = 0, save_record: bool = False, key_1: str = None, key_2: str = None, **kwargs):
        '''
        init data.

        Attributes:
            groud_truth (GroundTruth): whether to save the record data.
            min_confidence (float): if the result has lower confidence than min confidence, it will not be saved.
            top_k (int): the max number of result to be saved.
            save_record (bool): whether to save the record data.
            key_1 (String): the attribute in first record be compared.
            key_2 (String): the attribute in second record be compared.
        '''
        self._ground_truth = groud_truth
        self._min_confidence = min_confidence
        self.label = label
        self._top_k = top_k

        self._data = []  # trial results
        self.save_record = save_record
        self.key_1 = key_1
        self.key_2 = key_2
        self.evaluator = None
        self.self_defined_key_values = kwargs

    def add_result(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None) -> None:
        '''
        Add one pair record comparison result.
        If confidence is less than min_confidence, it will skip.
        If confidence is less than the least confidence saved item and there are top_k items, it will skip.
        If confidence is more than the least confidence saved item and there are top_k items, the least confidence saved item will be removed and then save the current one.
        If it is not full, it wll directly save the current one.

        Attributes:
            record1 (Record): first record.
            record2 (Record): second record.
            is_positive (bool): the result of similarity function.
            confidence (float): = how much confidence the similarity function has on the result.
        '''
        if confidence >= self._min_confidence and self._ground_truth.is_member(record1.id, record2.id):
            if self._top_k == 0 or len(self._data) < self._top_k:
                cur = self.TrialResult(record1, record2, is_positive, confidence, self.save_record, self.key_1,
                                       self.key_2)
                heapq.heappush(self._data, cur)
            elif confidence > self._data[0].confidence:
                heapq.heappop(self._data)
                cur = self.TrialResult(record1, record2, is_positive, confidence, self.save_record, self.key_1,
                                       self.key_2)
                heapq.heappush(self._data, cur)

    def add_positive(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=True, **kwargs)

    def add_negative(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=False, **kwargs)

    def get_all_data(self):
        '''
        get all saved data

        Returns:
            data (list)
        '''
        return self._data

    def get_ground_truth(self):
        '''
        get saved ground truth

        Returns:
            ground_truth (GroundTruth)
        '''
        return self._ground_truth

    def evaluate(self):
        self.evaluator = self.SelfEvaluation()
        self.evaluator.evaluate(self._ground_truth, self._data)

    def __getattr__(self, key):
        return self.self_defined_key_values[key]

    @property
    def precision(self) -> float:
        '''
        Based on the mathematical formula:
            precision = true positive / (true positive + false positive)
        Calculate and return the precision

        Returns:
            precision (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.precision()

    @property
    def recall(self) -> float:
        '''
        return the true positive ratio

        Returns:
            recall (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.recall()

    @property
    def f_measure(self) -> float:
        '''
        Based on the mathematical formula:
            f_measure = 2 * true positive / (2 * true positive + false positive + false negative)
        Calculate and return the f_measure

        Returns:
            f_measure (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.f_measure()

    @property
    def false_positives(self) -> float:
        '''
        Based on the mathematical formula:
            false positive ratio = false positive / (false positive + true negative)
        Calculate and return the false positive ratio

        Returns:
            false positive ratio (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.false_positives()

    @property
    def true_positives(self) -> float:
        '''
        Based on the mathematical formula:
            true positive ratio = true positive / (true positive + false negative)
        Calculate and return the true positive ratio

        Returns:
            true positive ratio (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.true_positives()

    @property
    def false_negatives(self) -> float:
        '''
        Based on the mathematical formula:
            false negative ratio = false negative / (false negative + true positive)
        Calculate and return the false negative ratio

        Returns:
            false negative ratio (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.false_negatives()

    @property
    def true_negatives(self) -> float:
        '''
        Based on the mathematical formula:
            true negative ratio = true negative / (true negative + false positive)
        Calculate and return the true negative ratio

        Returns:
            true negative ratio (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.true_negatives()

    @property
    def false_discovery(self):
        '''
        Based on the mathematical formula:
            false discovery = false positive / (false positive + true positive)
        Calculate and return the false false discovery

        Returns:
            false discovery (float)
        '''
        self.checkEvaluatorInit()
        return self.evaluator.false_discovery()

    def checkEvaluatorInit(self):
        if self.evaluator == None:
            raise Exception("Not evaluate, run evaluation function firstly")

    def __str__(self):
        res = json.dump(self._data)
        return res

    def __repr__(self):
        pass

# print all saved data
# get_record(tp, dataset_1, ds_@)
