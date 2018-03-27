from rltk.record import Record
import json

class GroundTruth(object):
    __ground_trurh_data = None

    def __init__(self):
        self.__ground_trurh_data = {}
        pass

    def add_positive(self, record1: Record, record2: Record):
        self.add_ground_truth(record1, record2, True)
        pass

    def add_negative(self, record1: Record, record2: Record):
        self.add_ground_truth(record1, record2, False)
        pass

    def add_ground_truth(self, record1: Record, record2: Record, value: bool):
        key = self.gen_key(record1, record2)
        self.__ground_trurh_data[key] = value

    def is_member(self, record1: Record, record2: Record) -> bool:
        key = self.gen_key(record1, record2)
        return key in self.__ground_trurh_data

    def is_positive(self, record1: Record, record2: Record) -> bool:
        key = self.gen_key(record1, record2)
        if self.__is_member(key):
            return self.__ground_trurh_data[key]
        else:
            raise Exception("not a member")

    def is_negative(self, record1: Record, record2: Record) -> bool:
        key = self.gen_key(record1, record2)
        if self.__is_member(key):
            return not self.__ground_trurh_data[key]
        else:
            raise Exception("not a member")

    def load(self, filename):
    #this will overwrite the current self.ground_trurh
        with open(filename, 'r') as f:
            self.__ground_trurh_data = json.load(f)

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.__ground_trurh_data, f)

    def gen_key(self, record1: Record, record2: Record):
        key = "" + record1.__str__() + "|" + record2.__str__()
        return key

    def __is_member(self, key: str) -> bool:
        return key in self.__ground_trurh_data
