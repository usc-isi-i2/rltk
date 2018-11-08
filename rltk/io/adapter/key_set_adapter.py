import json
import io


class KeySetAdapter(object):
    """
    Key Set Adapter.
    """

    def get(self, key: str):
        """
        Get value by key.
        
        Args:
            key (str): Key.
            
        Returns:
            set: A set of values, None if key doesn't exist.
        """
        raise NotImplementedError

    def set(self, key: str, value: set):
        """
        Set a set by key.
        
        Args:
            key (str): Key.
            value (builtins.set): Value set.
        """
        raise NotImplementedError

    def add(self, key: str, value: object):
        """
        Add value to a set by key. If key doesn't exist, create one.
        
        Args:
            key (str): Key.
            value (object): Value.
        """
        raise NotImplementedError

    def remove(self, key: str, value: object):
        """
        Remove value from a set by key. If key doesn't exist, create one.
        
        Args:
            key (str): Key.
            value (object): Value.
        """
        raise NotImplementedError

    def delete(self, key: str):
        """
        Delete a set by key.
        
        Args:
            key (str): Key.
        """
        raise NotImplementedError

    def dump(self, f: io.IOBase):
        """
        Dump data to json lines format. Each json object is formatted as `{key: [value1, value2, ...]}`.
        
        Args:
            f (io.IOBase): IO handler.
        """
        for k, ss in self:
            obj = {k: list(ss)}
            f.write(json.dumps(obj) + '\n')

    def clean(self):
        """
        Delete all keys in this adapter.
        """
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
            iter: key, set
        """
        pass

    def close(self):
        """
        Close handler if needed.
        """
        pass
