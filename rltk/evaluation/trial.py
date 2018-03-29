import json
import heapq

from rltk.record import Record
from rltk.evaluation.ground_truth import GroundTruth


class Trial(object):
    class TrialResult:
        def __init__(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None):
            self.record1 = record1
            self.record2 = record2
            self.is_positive = is_positive
            self.confidence = confidence

        def __cmp__(self, other):
            return self.confidence < other.confidence

        def __lt__(self, other):
            return self.confidence < other.confidence

    def __init__(self, groud_truth: GroundTruth, min_confidence: float = 0, top_k: int = 0):
        self.__ground_truth = groud_truth
        self.__min_confidence = min_confidence
        self.__top_k = top_k

        self.__data = []

    def add_result(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None) -> None:
        if confidence >= self.__min_confidence and self.__ground_truth.is_member(record1, record2):
            if self.__top_k == 0 or len(self.__data) < self.__top_k:
                cur = self.TrialResult(record1, record2, is_positive, confidence)
                heapq.heappush(self.__data, cur)
            elif confidence > self.__data[0].confidence:
                heapq.heappop(self.__data)
                cur = self.TrialResult(record1, record2, is_positive, confidence)
                heapq.heappush(self.__data, cur)

    def add_positive(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=True, **kwargs)

    def add_negative(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=False, **kwargs)

    def get_all_data(self):
        return self.__data

    def get_ground_truth(self):
        return self.__ground_truth

    def __str__(self):
        res = json.dump(self.__data)
        return res

    def __repr__(self):
        pass
