import __builtin__
__builtin__.rltk = {
    'enable_cython': False
}

import importlib

def init(enable_cython=False):
    """
    Initialization method.

    Args:
        enable_cython (bool, optional): Enable using cython module. Defaults to False.

    Returns:
        object: RLTK object
    """
    if enable_cython:
        __builtin__.rltk['enable_cython'] = True

    import core
    return core.Core()
