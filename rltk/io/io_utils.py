import io


def get_file_handler(f, mode='r'):
    """
    Helper function for getting file handler.

    Args:
        f (Union[str,io.IOBase]): File path or handler.
        mode (str, optional): Parameter mode in :py:meth:`open`. Defaults to `r`.

    Returns:
        io.IOBase: File handler.
    """
    if isinstance(f, io.IOBase):
        return f

    return open(f, mode)
