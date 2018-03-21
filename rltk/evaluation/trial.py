from rltk.record import Record
from rltk.evaluation.ground_truth import GroundTruth

class Trial(object):

    def __init__(name, groud_truth: GroundTruth, min_confidence: int, top_k: int):
        pass


    def add_result(self, record1: Record, record2: Record, is_positive: bool, confidence: float = None) -> None:
        pass

    def add_positive(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=True, **kwargs)

    def add_negative(self, kwargs):
        """syntactic sugar"""
        self.add_result(is_positive=False, **kwargs)

    def __str__(self):
        pass

    def __repr__(self):
        pass