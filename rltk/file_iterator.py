import json
from jsonpath_rw import parse

class FileIterator(object):

    _file_handler = None
    _count = 0
    _type = None

    def __init__(self, file_path, type='text', **kwargs):
        self._file_handler = open(file_path, 'r')
        self._type = type

        if type == 'json_line':
            # pre-compile id_path
            if 'id_path' in kwargs:
                self._id_path_parser = parse(kwargs['id_path'])
        else: # text
            pass


    def __iter__(self):
        return self

    def next(self):
        """
        Returns:
            misc, dict: object id, value
        """
        try:
            line = self._file_handler.next()
            oid = self._count

            if self._type == 'json_line':
                line = json.loads(line)
                if hasattr(self, '_id_path_parser'):
                    matches = self._id_path_parser.find(line)
                    extracted_id = [match.value for match in matches]
                    if len(extracted_id) == 0:
                        raise ValueError('Can\'t find id in json line file by id_path')
                        oid = extracted_id[0]

            self._count += 1
            return oid, line

        except StopIteration as e:
            self._file_handler.close()
            raise e

    def __del__(self):
        try:
            self._file_handler.close()
        except:
            pass
