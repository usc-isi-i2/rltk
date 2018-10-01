import os
import glob

from dask.distributed import Client


class Remote(object):

    def __init__(self, *args, **kwargs):
        # TODO: authentication
        # http://distributed.dask.org/en/latest/tls.html?highlight=security
        self._client = Client(*args, **kwargs)

    def add_dependencies(self, files):
        # TODO: automatically resolve module dependencies
        if isinstance(files, str):
            files = [files]
        for f in files:
            self._client.upload_file(f)

    def scatter(self, *args, **kwargs):
        return self._client.scatter(*args, **kwargs)

    def submit(self, func, *args, **kwargs):
        return self._client.submit(func, *args, **kwargs)

    def fetch(self, futures, **kwargs):
        return self._client.gather(futures, **kwargs)

    def cancel(self, futures, **kwargs):
        return self._client.cancel(futures, **kwargs)

    def close(self, *args, **kwargs):
        return self._client.close(*args, **kwargs)

    # @staticmethod
    # def _list_local_dir(pathname='**', *args, recursive=True):
    #     non_py_files = []
    #     py_files = []
    #     for path in glob.glob(pathname, *args, recursive=recursive):
    #         if os.path.isdir(path):
    #             if path == '__pycache__':
    #                 continue
    #         elif os.path.isfile(path):
    #             if path.endswith('.pyc'):
    #                 continue
    #             if path.endswith('.py'):
    #                 py_files.append(path)
    #             else:
    #                 non_py_files.append(path)
    #
    #     return non_py_files + py_files
