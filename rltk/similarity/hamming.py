import rltk.utils as utils


def hamming_distance(s1, s2):
    """
    Hamming distance used to measure the minimum number of substitutions required to change one sequence into the
    other.

    Args:
        s1 (str or list): Sequence 1.
        s2 (str or list): Sequence 2.

    Returns:
        int: Hamming distance between two sequences.

    Examples:
        >>> rltk.hamming_distance('ab','cd')
        2
        >>> rltk.hamming_distance([1,2,3],[3,2,3])
        1
    """

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
    """
    Hamming similarity is computed as 1 - normalized_hamming_distance.

    Args:
        s1 (str or list): Sequence 1.
        s2 (str or list): Sequence 2.

    Returns:
        float: Hamming similarity.

    Examples:
        >>> rltk.hamming_similarity('ab','cd')
        0
        >>> rltk.hamming_similarity([1,2,3],[3,2,3])
        0.666666666667
    """

    return 1 - normalized_hamming_distance(s1, s2)
