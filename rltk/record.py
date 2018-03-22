
class Record(object):
    def __init__(self, raw_object):
        self.raw_object = raw_object

    @property
    def id(self):
        """return has to be utf-8 string"""
        raise NotImplementedError
