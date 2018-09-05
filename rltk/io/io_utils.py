import io


def get_file_handler(f):
    """
    Helper function for getting file handler.

    Args:
        f (Union[str,io.IOBase]): File path or handler.

    Returns:
        io.IOBase: File handler.
    """
    if isinstance(f, io.IOBase):
        return f

    return open(f, 'w')
