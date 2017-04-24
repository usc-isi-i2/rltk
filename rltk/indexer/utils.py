from jsonpath_rw import parse
from jsonpath_rw.jsonpath import Fields

"""
  Helper method to extract data from json data

  Args:
    data(json) : nested json document
    keys(list) : list of keys to be extracted from json document
    parse_dict(:obj: `dict`, optional) : keys and jsonpath_parse_object for the key in the document 

  Returns:
    dict: key value pair

"""
def extract(data, keys, parse_dict=None):
  if parse_dict is None:
    parse_dict = {}
    for k in keys:
      parse_dict[k] = parse(k)
  extracted_values = {}
  for k in keys:
    extracted_values[k] = [match.value for match in parse_dict[k].find(data)]
  return extracted_values