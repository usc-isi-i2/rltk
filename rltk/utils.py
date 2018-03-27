import unicodedata


def check_for_none(*args):
    for arg in args:
        if arg is None:
            raise ValueError('Missing parameter')


def check_for_type(type, *args):
    for arg in args:
        if not isinstance(arg, type):
            raise TypeError('Wrong type of parameter')


def unicode_normalize(s):
    return unicodedata.normalize('NFKD', s)


def convert_list_to_set(s):
    if isinstance(s, list):
        s = set(s)
    return s
