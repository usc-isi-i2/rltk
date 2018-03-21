
class Record(object):
    def __init__(self, raw_object):
        self.raw_object = raw_object

    @property
    def id(self):
        raise NotImplementedError
