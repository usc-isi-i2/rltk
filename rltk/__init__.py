import __builtin__
__builtin__.rltk = {
    'enable_cython': False
}

import core

def enable_cython(enable=False):
    """
    Enable cython support. It's a global change.
    """
    __builtin__.rltk['enable_cython'] = enable
    reload(core)

def init(enable_cython=False):
    """
    Initialization method.

    Returns:
        object: RLTK object
    """
    return core.Core()
