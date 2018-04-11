import json

from rltk.io.reader import GroundTruthReader
from rltk.io.writer import GroundTruthWriter


class GroundTruth(object):
    ID1 = 'id1'
    ID2 = 'id2'
    LABEL = 'label'

    def __init__(self):
        self.__ground_trurh_data = {}
        pass

    def add_positive(self, id1: str, id2: str):
        self.add_ground_truth(id1, id2, True)
        pass

    def add_negative(self, id1: str, id2: str):
        self.add_ground_truth(id1, id2, False)
        pass

    def add_ground_truth(self, id1: str, id2: str, value: bool):
        key = self.gen_key(id1, id2)
        self.__ground_trurh_data[key] = value

    def is_member(self, id1: str, id2: str) -> bool:
        key = self.gen_key(id1, id2)
        return key in self.__ground_trurh_data

    def is_positive(self, id1: str, id2: str) -> bool:
        key = self.gen_key(id1, id2)
        if self.__is_member(key):
            return self.__ground_trurh_data[key]
        else:
            raise Exception("not a member")

    def is_negative(self, id1: str, id2: str) -> bool:
        key = self.gen_key(id1, id2)
        if self.__is_member(key):
            return not self.__ground_trurh_data[key]
        else:
            raise Exception("not a member")

    def load(self, filename):
        # this will overwrite the current self.ground_trurh
        for obj in GroundTruthReader(filename):
            self.__ground_trurh_data[self.gen_key(obj[self.ID1], obj[self.ID2])] = obj[self.LABEL] == 'True'

    def save(self, filename):
        w = GroundTruthWriter(filename)
        for k, v in self.__ground_trurh_data.items():
            ids = json.loads(k)
            w.write(ids[self.ID1], ids[self.ID2], v)
        w.close()

    def gen_key(self, id1: str, id2: str):
        key = json.dumps({self.ID1: id1, self.ID2: id2})
        return key

    def __is_member(self, key: str) -> bool:
        return key in self.__ground_trurh_data
