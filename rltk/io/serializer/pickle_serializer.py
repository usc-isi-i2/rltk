import pickle

from rltk.io.serializer import Serializer


class PickleSerializer(Serializer):
    """
    `Pickle serializer <https://docs.python.org/3/library/pickle.html>`_ .
    """

    def loads(self, string):
        return pickle.loads(string)

    def dumps(self, obj):
        return pickle.dumps(obj)
