from rltk.record import Record


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

    def get(self, record_id) -> Record:
        """
        Get record.
        
        Args:
            record_id (str): Record id.
            
        Returns:
            Record:
        """
        raise NotImplementedError

    def set(self, record_id, record: Record):
        """
        Set record.
        
        Args:
            record_id (str): Record id.
            record (Record): Record object.
        """
        raise NotImplementedError

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