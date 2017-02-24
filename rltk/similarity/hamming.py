import utils

def hamming_distance(s1, s2):
    """
    Hamming distance used to measure the minimum number of substitutions required to change one sequence into the
    other.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        int: Hamming distance between two sequences.

    Examples:
        >>> rltk.hamming_distance('ab','cd')
        2
        >>> rltk.hamming_distance('ab','bc')
        2
        >>> rltk.hamming_distance('ab','ab')
        0
    """

    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    if len(s1) != len(s2):
        raise ValueError('Unequal length')

    return sum(c1 != c2 for c1, c2 in zip(s1, s2))