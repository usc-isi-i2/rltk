class Record(object):

    def __init__(self, raw_object):
        self.raw_object = raw_object

    @property
    def id(self):
        """return has to be utf-8 string"""
        raise NotImplementedError


class cached_property(property):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        """
        :param obj: Record instance
        :param cls: Record class
        """
        if obj is None:
            return self

        cached_name = '_c_' + self.func.__name__
        if cached_name not in obj.__dict__:
            obj.__dict__[cached_name] = self.func(obj)
        value = obj.__dict__.get(cached_name)
        return value


def generate_record_property_cache(obj, remove_raw_object=False):
    for method_name in dir(obj):
        if not method_name.startswith('__'):
            # if the method is a normal function, it only returns function reference
            # if it's a property, if will be invoked and returns the property value
            # so if it's (cached_property) decorated, the cache will be generated
            getattr(obj, method_name)

    if 'raw_object' in obj.__dict__ and remove_raw_object:
        del obj.__dict__['raw_object']
