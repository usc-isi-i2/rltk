class Serializer(object):
    """
    Serialize and deserialize object. This is the super class.
    """

    def loads(self, obj):
        """
        Load a serialized object.
         
        Args:
            obj (obj): For most of times, it's byte or string.
            
        Returns:
            obj: Python object.
        """
        raise NotImplementedError

    def dumps(self, obj):
        """
        Serialize the given object.
        
        Args:
            obj (obj): Python object.
            
        Returns:
            obj: Serialized object.
        """
        raise NotImplementedError
