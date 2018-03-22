import rltk.utils as utils


def hamming_distance(s1, s2):

    utils.check_for_none(s1, s2)
    # utils.check_for_type(str, s1, s2)

    if len(s1) != len(s2):
        raise ValueError('Unequal length')

    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def normalized_hamming_distance(s1, s2):

    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0

    distance = hamming_distance(s1, s2)
    return float(distance) / max_len


def hamming_similarity(s1, s2):

    return 1 - normalized_hamming_distance(s1, s2)
