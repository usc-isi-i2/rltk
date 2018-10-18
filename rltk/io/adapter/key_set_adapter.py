import json


class KeySetAdapter(object):

    def get(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def add(self, key, value):
        raise NotImplementedError

    def remove(self, key, value):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def dump(self, f):
        for k, ss in self:
            obj = {k: list(ss)}
            f.write(json.dumps(obj) + '\n')

    def clean(self):
        for k, _ in self:
            self.delete(k)

    def __init__(self):
        pass

    def __del__(self):
        """
        Same as :meth:`close`.
        """
        self.close()

    def __iter__(self):
        """
        Same as :meth:`__next__`.
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator of the data store. This is not required.

        Returns:
            iter: record_id, record
        """
        pass

    def close(self):
        """
        Close handler if needed.
        """
        pass
