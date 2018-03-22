import pickle

from rltk.io.serializer import Serializer


class PickleSerializer(Serializer):

    def loads(self, string):
        return pickle.loads(string)

    def dumps(self, obj):
        return pickle.dumps(obj)
