import math
from .. import utils


def cosine_similarity(vec1, vec2):

    utils.check_for_none(vec1, vec2)
    utils.check_for_type(list, vec1, vec2)

    v_x_y, v_x_2, v_y_2 = 0.0, 0.0, 0.0
    for v1, v2 in zip(vec1, vec2): # list of int / float
        v_x_y += v1 * v2
        v_x_2 += v1 * v1
        v_y_2 += v2 * v2

    return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))
