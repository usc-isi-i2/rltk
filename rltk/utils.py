import unicodedata
from jsonpath_rw import parse

def check_for_none(*args):
    for arg in args:
        if arg is None:
            raise ValueError('Missing parameter')


def check_for_type(type, *args):
    for arg in args:
        if not isinstance(arg, type):
            raise TypeError('Wrong type of parameter')


def unicode_normalize(s):
    if isinstance(s, unicode):
        s = unicodedata.normalize('NFKD', s)
    return s


def convert_list_to_set(s):
    if isinstance(s, list):
        s = set(s)
    return s


def extract(data, keys, parse_dict=None):
    """
      Helper method to extract data from json data

      Args:
        data(json) : nested json document
        keys(list) : list of keys to be extracted from json document
        parse_dict(:obj: `dict`, optional) : keys and jsonpath_parse_object for the key in the document

      Returns:
        dict: key value pair

    """
    if parse_dict is None:
        parse_dict = {}
        for k in keys:
            parse_dict[k] = parse(k)
    extracted_values = {}
    for k in keys:
        extracted_values[k] = [match.value for match in parse_dict[k].find(data)]
    return extracted_values
