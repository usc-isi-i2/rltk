import json
import heapq

from rltk.record import Record
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

    def __init__(self, groud_truth: GroundTruth, min_confidence: float = 0, top_k: int = 0, save_record: bool = False,
                 key_1: str = None, key_2: str = None):
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
        self.__ground_truth = groud_truth
        self.__min_confidence = min_confidence
        self.__top_k = top_k

        self.__data = []
        self.save_record = save_record
        self.key_1 = key_1
        self.key_2 = key_2

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
        if confidence >= self.__min_confidence and self.__ground_truth.is_member(record1.id, record2.id):
            if self.__top_k == 0 or len(self.__data) < self.__top_k:
                cur = self.TrialResult(record1, record2, is_positive, confidence, self.save_record, self.key_1,
                                       self.key_2)
                heapq.heappush(self.__data, cur)
            elif confidence > self.__data[0].confidence:
                heapq.heappop(self.__data)
                cur = self.TrialResult(record1, record2, is_positive, confidence, self.save_record, self.key_1,
                                       self.key_2)
                heapq.heappush(self.__data, cur)

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
        return self.__data

    def get_ground_truth(self):
        '''
        get saved ground truth

        Returns:
            ground_truth (GroundTruth)
        '''
        return self.__ground_truth

    def __str__(self):
        res = json.dump(self.__data)
        return res

    def __repr__(self):
        pass

# print all saved data
# get_record(tp, dataset_1, ds_@)
