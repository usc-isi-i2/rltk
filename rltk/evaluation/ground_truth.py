from rltk.evaluation.trial import Trial
from rltk.record import Record
import json

class GroundTruth(object):
    __ground_trurh = None

    def __init__(self, filename=None):
        self.ground_trurh = {}
        pass

    def add_positive(self, record1: Record, record2: Record):
        self.add_ground_truth(record1, record2, True)
        pass

    def add_negative(self, record1: Record, record2: Record):
        self.add_ground_truth(record1, record2, False)
        pass

    def add_ground_truth(self, record1: Record, record2: Record, value: bool):
        key = self.__gen_key(record1, record2)
        self.ground_trurh[key] = value

    def is_member(self, record1: Record, record2: Record) -> bool:
        key = self.__gen_key(record1, record2)
        return key in self.ground_trurh

    def is_positive(self, record1: Record, record2: Record) -> bool:
        key = self.gen_key(record1, record2)
        if self.is_member(key):
            return self.ground_trurh[key]
        else:
            raise Exception("not a member")

    def is_negative(self, record1: Record, record2: Record) -> bool:
        key = self.__gen_key(record1, record2)
        if self.is_member(key):
            return not self.ground_trurh[key]
        else:
            raise Exception("not a member")

    def load(self, filename):
    #this will overwrite the current self.ground_trurh
        with open(filename, 'r') as f:
            self.ground_trurh = json.load(f)

    def save(self, filename):
        pass

    def __gen_key(self, record1: Record, record2: Record):
        key = "" + record1 + "|" + record2
        return key

    def __is_member(self, key: str) -> bool:
        return key in self.ground_trurh
