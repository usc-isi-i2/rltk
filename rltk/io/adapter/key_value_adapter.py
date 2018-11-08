class KeyValueAdapter(object):
    """
    Super class of adapter of key value stores.
    """
    def __init__(self):
        pass

    def __del__(self):
        """
        Same as :meth:`close`.
        """
        self.close()

    #: If this adapter is parallel-safe. Defaults to False if it's not overwritten in concrete class.
    parallel_safe = False

    def get(self, key: str) -> object:
        """
        Get value.
        
        Args:
            key (str): Key. 
            
        Returns:
            object:
        """
        raise NotImplementedError

    def set(self, key: str, value: object):
        """
        Set value.
        
        Args:
            key (str): Key.
            value (object): Value.
        """
        raise NotImplementedError

    def delete(self, key):
        """
        Delete value.
        
        Args:
            key (str): Key.
        """
        raise NotImplementedError

    def clean(self):
        """
        Delete all keys in adapter.
        """
        for key in self:
            self.delete(key)

    def __iter__(self):
        """
        Same as :meth:`__next__`.
        """
        return self.__next__()

    def __next__(self):
        """
        Iterator of the data store. This is not required.
        
        Returns:
            iter: key, value 
        """
        pass

    def close(self):
        """
        Close handler if needed.
        """
        pass