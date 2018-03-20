from rltk.evaluation.trial import Trial
from rltk.record import Record


class GroundTruth(object):
    def __init__(self, filename=None):
        pass

    def add_positive(self, record1: Record, record2: Record):
        pass

    def add_negative(self, record1: Record, record2: Record):
        pass

    def is_member(self, record1: Record, record2: Record) -> bool:
        pass

    def is_positive(self, record1: Record, record2: Record) -> bool:
        pass

    def is_negative(self, record1: Record, record2: Record) -> bool:
        pass

    def load(self, filename):
        pass

    def save(self, filename):
        pass
