import os
import glob
from distributed import Worker

from dask.distributed import Client
from distributed.security import Security


class Remote(object):
    """
    Remote.
    
    Args:
        address (str): Remote scheduler address formed by `ip:port`.
        tls_ca_file (str, optional): TLS CA certificate file path. Defaults to None.
        tls_client_cert (str, optional): TLS certificate file path. Defaults to None.
        tls_client_key (str, optional): TLS private key file path. Defaults to None.
        require_encryption (bool, optional): Encrypt data exchange. Defaults to False.
        
    Note:
        TLS will be enabled only if all three TLS arguments are provided. 
        Remember to change network protocol to `tls://<address>`.
    """
    def __init__(self, address: str,
                 tls_ca_file: str = None, tls_client_cert: str = None, tls_client_key: str = None,
                 require_encryption: bool = False):
        # authentication
        sec = None
        if tls_ca_file and tls_client_cert and tls_client_key:
            sec = Security(tls_ca_file=tls_ca_file,
                           tls_client_cert=tls_client_cert,
                           tls_client_key=tls_client_key,
                           require_encryption=require_encryption)

        # init
        self._client = Client(address=address, security=sec)
        self._client.register_worker_callbacks(Remote._worker_startup)

    @staticmethod
    def _worker_startup(dask_worker: Worker):
        os.chdir(dask_worker.local_dir)

    def add_dependencies(self, files):
        """
        Add list of dependencies, order matters.
        
        Args:
            files (list): List of dependent files.
        """
        # TODO: automatically resolve module dependencies
        if isinstance(files, str):
            files = [files]
        for f in files:
            self._client.upload_file(f)

    def scatter(self, *args, **kwargs):
        """
        Scatter data.
        """
        return self._client.scatter(*args, **kwargs)

    def submit(self, func, *args, **kwargs):
        """
        Submit function and data.
        
        Args:
            func (callable): User function.
        """
        return self._client.submit(func, *args, **kwargs)

    def fetch(self, futures_, **kwargs):
        """
        Fetch data of future objects.
        
        Args:
            futures_ (list): Future objects.
        """
        return self._client.gather(futures_, **kwargs)

    def cancel(self, futures_, **kwargs):
        """
        Cancel job of future objects.
        
        Args:
            futures_ (list): Future objects.
        """
        return self._client.cancel(futures_, **kwargs)

    def close(self, *args, **kwargs):
        """
        Close connection.
        """
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
