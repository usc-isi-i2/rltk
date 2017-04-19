import json
import csv
import hashlib
import itertools

from jsonpath_rw import parse


class FileIterator(object):

    _file_path = None
    _type = None
    _kwargs = {}
    _file_handler = None
    _count = 0

    def __init__(self, file_path, type='text', **kwargs):
        self._file_path = file_path
        self._type = type
        self._kwargs = kwargs
        self._file_handler = open(file_path, 'r')

        if type == 'json_line':
            # pre-compile json path, raise exception if not exists
            self._id_path_parser = parse(kwargs['id_path'])
            self._value_path_parser = parse(kwargs['value_path'])
        elif type == 'csv':
            self._id_column = kwargs['id_column'] # raise exception if not exists
            self._value_columns = kwargs['value_columns']
            delimiter = kwargs['delimiter'] if 'delimiter' in kwargs else ','
            quotechar = kwargs['quotechar'] if 'quotechar' in kwargs else '"'
            quoting = kwargs['quoting'] if 'quoting' in kwargs else csv.QUOTE_MINIMAL
            field_names = kwargs['field_names'] if 'field_names' in kwargs else None
            self._csv_reader = csv.DictReader(
                self._file_handler, delimiter=delimiter, quotechar=quotechar, quoting=quoting, fieldnames=field_names)
        else: # text
            self._id_prefix = hashlib.md5(file_path).hexdigest()[:6]

    def __copy__(self):
        """
            Clone the iterator include states
        """
        # https://docs.python.org/2/library/itertools.html#itertools.tee
        # tee is not that helpful here, and it will also occupy a lot of memory
        # self._file_handler, new_iter = itertools.tee(self._file_handler)

        new_iter = FileIterator(self._file_path, self._type, **self._kwargs)
        for _ in new_iter:
            if new_iter._count == self._count:
                break
        return new_iter

    def copy(self):
        return self.__copy__()

    def next(self):
        """
        Returns:
            str, dict: object id, value
        """
        try:
            oid, value = None, None
            if self._type == 'json_line':
                line = next(self._file_handler)
                line = json.loads(line)

                matches = self._id_path_parser.find(line)
                extracted_id = [match.value for match in matches]
                if len(extracted_id) == 0:
                    raise ValueError('Can\'t find id in json line file by id_path')
                oid = extracted_id[0]

                matches = self._value_path_parser.find(line)
                extracted_value = [match.value for match in matches]
                if len(extracted_value) == 0:
                    raise ValueError('Can\'t find value in json line file by value_path')
                value = extracted_value
            elif self._type == 'csv':
                line = self._csv_reader.next()
                oid = line[self._id_column]
                value = [line[k] for k in self._value_columns]
            else: # text
                line = self._file_handler.next()
                line = line.strip('\n')
                oid = self._id_prefix + '-' + str(self._count)
                value = [line]

            self._count += 1
            # id should be a string
            if isinstance(oid, int):
                oid = 'int-' + str(oid)
            return oid, value

        except StopIteration as e:
            # self._file_handler.close()
            raise e

    def __iter__(self):
        return self

    def __del__(self):
        try:
            pass
            # self._file_handler.close()
        except:
            pass
