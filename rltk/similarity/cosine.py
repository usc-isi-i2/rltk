import math
import collections
import rltk.utils as utils


def cosine_similarity(vec1, vec2):
    """
    The cosine similarity between to vectors.

    Args:
        vec1 (list): Vector 1. List of integer or float.
        vec2 (list): Vector 2. List of integer or float. It should have the same length to vec1.

    Returns:
        float: Cosine similarity.

    Examples:
        >>> rltk.cosine_similarity([1, 2, 1, 3], [2, 5, 2, 3])
        0.91634193
    """

    utils.check_for_none(vec1, vec2)
    utils.check_for_type(list, vec1, vec2)
    if len(vec1) != len(vec2):
        raise ValueError('vec1 and vec2 should have same length')

    v_x_y, v_x_2, v_y_2 = 0.0, 0.0, 0.0
    for v1, v2 in zip(vec1, vec2):  # list of int / float
        v_x_y += v1 * v2
        v_x_2 += v1 * v1
        v_y_2 += v2 * v2

    return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))


def string_cosine_similarity(bag1, bag2):
    """
    The similarity between the two strings is the cosine of the angle between these two vectors representation.

    Args:
        bag1 (list): Bag1, tokenized string sequence.
        bag2 (list): Bag2, tokenized string sequence.

    Returns:
        float: Cosine similarity.
    """

    utils.check_for_none(bag1, bag2)
    utils.check_for_type(list, bag1, bag2)

    d1 = collections.Counter(bag1)
    d2 = collections.Counter(bag2)

    intersection = set(d1.keys()) & set(d2.keys())
    v_x_y = sum([d1[x] * d2[x] for x in intersection])
    v_x_2 = sum([v * v for k, v in d1.items()])
    v_y_2 = sum([v * v for k, v in d2.items()])

    return 0.0 if v_x_y == 0 else float(v_x_y) / (math.sqrt(v_x_2) * math.sqrt(v_y_2))
