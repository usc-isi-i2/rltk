import utils

def hamming_distance(s1, s2):
    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    if len(s1) != len(s2):
        raise ValueError('Unequal length')

    return sum(c1 != c2 for c1, c2 in zip(s1, s2))