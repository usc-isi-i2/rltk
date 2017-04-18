import json
import csv
from jsonpath_rw import parse

class FileIterator(object):

    _file_handler = None
    _count = 0
    _type = None

    def __init__(self, file_path, type='text', **kwargs):
        self._file_handler = open(file_path, 'r')
        self._type = type

        if type == 'json_line':
            # pre-compile id_path, raise exception if not exists
            self._id_path_parser = parse(kwargs['id_path'])
        elif type == 'csv':
            self._id_column = kwargs['id_column'] # raise exception if not exists
            delimiter = kwargs['delimiter'] if 'delimiter' in kwargs else ','
            quotechar = kwargs['quotechar'] if 'quotechar' in kwargs else '"'
            quoting = kwargs['quoting'] if 'quoting' in kwargs else csv.QUOTE_MINIMAL
            field_names = kwargs['field_names'] if 'field_names' in kwargs else None
            self._csv_reader = csv.DictReader(
                self._file_handler, delimiter=delimiter, quotechar=quotechar, quoting=quoting, fieldnames=field_names)
        else: # text
            pass

    def next(self):
        """
        Returns:
            misc, dict: object id, value
        """
        try:
            if self._type == 'json_line':
                line = self._file_handler.next()
                line = json.loads(line)
                matches = self._id_path_parser.find(line)
                extracted_id = [match.value for match in matches]
                if len(extracted_id) == 0:
                    raise ValueError('Can\'t find id in json line file by id_path')
                oid = extracted_id[0]
            elif self._type == 'csv':
                line = self._csv_reader.next()
                oid = line[self._id_column]
            else: # text
                line = self._file_handler.next()
                line = line.strip('\n')
                oid = self._count
                line = {'id': oid, 'text': line}

            self._count += 1
            return oid, line

        except StopIteration as e:
            self._file_handler.close()
            raise e

    def __iter__(self):
        return self

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
