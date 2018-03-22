import math
import collections
import rltk.utils as utils


def cosine_similarity(vec1, vec2):
    """
    vec1 & vec2 should have same length and the type of element in vector should be int / float.
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
    utils.check_for_none(bag1, bag2)
    utils.check_for_type(list, bag1, bag2)

    d1 = collections.Counter(bag1)
    d2 = collections.Counter(bag2)

    intersection = set(d1.keys()) & set(d2.keys())
    v_x_y = sum([d1[x] * d2[x] for x in intersection])
    v_x_2 = sum([v * v for k, v in d1.items()])
    v_y_2 = sum([v * v for k, v in d2.items()])

    return 0.0 if v_x_y == 0 else float(v_x_y) / (math.sqrt(v_x_2) * math.sqrt(v_y_2))
