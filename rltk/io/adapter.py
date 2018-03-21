from rltk.record import Record


class Adapter(object):
    def __init__(self):
        pass

    def __del__(self):
        pass

    def get(self, record_id) -> Record:
        raise NotImplementedError

    def set(self, record_id, record: Record):
        raise NotImplementedError

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        """iterator is not required in adapter"""
        pass
