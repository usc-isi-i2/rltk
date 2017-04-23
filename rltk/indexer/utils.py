from jsonpath_rw import parse
from jsonpath_rw.jsonpath import Fields

"""
  Helper method to extract data from json data

  Args:
    data(json) : nested json document
    keys(list) : list of keys to be extracted from json document

  Returns:
    dict: key value pair

"""
def extract(data, keys):
  print(keys)
  parse_dict = {}
  for k in keys:
    parse_dict[k] = parse(k)
  extracted_values = {}
  for k in keys:
    extracted_values[k] = [match.value for match in parse_dict[k].find(data)]
  return extracted_values