class Reader(object):
    def __init__(self):
        pass

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        """return raw content of one record"""
        raise NotImplementedError

    def __del__(self):
        pass
