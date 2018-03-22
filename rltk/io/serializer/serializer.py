class Serializer(object):
    def loads(self, obj):
        raise NotImplementedError

    def dumps(self, obj):
        raise NotImplementedError
