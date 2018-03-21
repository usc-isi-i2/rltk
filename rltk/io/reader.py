import itertools


class Reader(object):
    def __init__(self):
        pass

    def __iter__(self):
        return self.__next__()

    def __next__(self):
        raise NotImplementedError

    def __del__(self):
        pass

    def __copy__(self):
        raise NotImplementedError

    def copy(self):
        return self.__copy__()
