# https://docs.scipy.org/doc/scipy-0.14.0/reference/spatial.distance.html
from scipy.spatial.distance import euclidean, cityblock

import rltk.utils as utils


def euclidean_distance(vec1, vec2, weights=None):
    """
    Euclidean distance.

    Args:
        vec1 (list): Vector 1. List of integer or float.
        vec2 (list): Vector 2. List of integer or float. It should have the same length to vec1.
        weights (list): Weights for each value in vectors. If it's None, all weights will be 1.0. Defaults to None.

    Returns:
        float: Euclidean distance.
    """

    utils.check_for_none(vec1, vec2)
    utils.check_for_type(list, vec1, vec2)
    if weights:
        utils.check_for_type(list, weights)
    if len(vec1) != len(vec2):
        raise ValueError('vec1 and vec2 should have same length')

    return euclidean(vec1, vec2, weights)


def euclidean_similarity(vec1, vec2, weights=None):
    """
    Computed as 1 / (1 + euclidean_distance)
    """
    return 1.0 / (1.0 + float(euclidean_distance(vec1, vec2, weights)))


def manhattan_distance(vec1, vec2, weights=None):
    """
    Manhattan distance.

    Args:
        vec1 (list): Vector 1. List of integer or float.
        vec2 (list): Vector 2. List of integer or float. It should have the same length to vec1.
        weights (list): Weights for each value in vectors. If it's None, all weights will be 1.0. Defaults to None.

    Returns:
        float: Manhattan distance.
    """
    utils.check_for_none(vec1, vec2)
    utils.check_for_type(list, vec1, vec2)
    if weights:
        utils.check_for_type(list, weights)
    if len(vec1) != len(vec2):
        raise ValueError('vec1 and vec2 should have same length')

    return cityblock(vec1, vec2, weights)


def manhattan_similarity(vec1, vec2, weights=None):
    """
    Computed as 1 / (1 + manhattan_distance)
    """
    return 1.0 / (1.0 + manhattan_distance(vec1, vec2, weights))
