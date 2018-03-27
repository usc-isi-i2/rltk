class Record(object):
    remove_raw_object = False

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
        Args:
            obj (object): Record instance
            cls (class): Record class
        Returns:
            object: cached value
        """
        if obj is None:
            return self

        # create property if it's not there
        cached_name = self.func.__name__
        if cached_name not in obj.__dict__:
            obj.__dict__[cached_name] = self.func(obj)

        value = obj.__dict__.get(cached_name)
        return value


def generate_record_property_cache(obj):
    """
    run getattr() on cached_property decorated methods to generate cache
    """
    for prop_name, prop_type in obj.__class__.__dict__.items():
        if isinstance(prop_type, cached_property):
            getattr(obj, prop_name)

    validate_record(obj)

    if obj.__class__.remove_raw_object:
        del obj.__dict__['raw_object']


def validate_record(obj):
    if not isinstance(obj.id, str):
        raise TypeError('Id in {} should be an utf-8 encoded string.'.format(obj.__class__.__name__))
