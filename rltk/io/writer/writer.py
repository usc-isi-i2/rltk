import io


class Writer(object):
    def __init__(self):
        pass

    def write(self):
        raise NotImplementedError

    def __del__(self):
        pass

    def close(self):
        self.__del__()

    @staticmethod
    def get_file_handler(f):
        if isinstance(f, io.IOBase):
            return f

        return open(f, 'w')
