import math
import rltk.utils as utils


def _jaro_winkler(s1, s2, threshold=0.7, scaling_factor=0.1, prefix_len=4):
    jaro = _jaro_distance(s1, s2)
    if jaro > threshold:
        l = min(len(_get_prefix(s1, s2)), prefix_len)  # max len of common prefix is 4
        jaro += (scaling_factor * l * (1.0 - jaro))
    return jaro


def jaro_winkler_similarity(s1, s2, threshold=0.7, scaling_factor=0.1, prefix_len=4):
    """
    The max length for common prefix is 4.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.
        threshold (int, optional): Boost threshold, prefix bonus is only added when compared strings have a Jaro Distance above it. Defaults to 0.7.
        scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards for having common prefixes. Defaults to 0.1.

    Returns:
        float: Jaro Winkler Similarity.

    Examples:
        >>> rltk.jaro_winkler_similarity('abchello', 'abcworld')
        0.6833333333333332
        >>> rltk.jaro_winkler_similarity('hello', 'world')
        0.4666666666666666
    """
    return _jaro_winkler(s1, s2, threshold, scaling_factor, prefix_len)


def jaro_winkler_distance(s1, s2, threshold=0.7, scaling_factor=0.1, prefix_len=4):
    """
    Jaro Winkler Distance is computed as 1 - jaro_winkler_similarity.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.
        threshold (int, optional): Boost threshold, prefix bonus is only added when compared strings have a Jaro Distance above it. Defaults to 0.7.
        scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards for having common prefixes. Defaults to 0.1.

    Returns:
        float: Jaro Winkler Similarity.

    Examples:
        >>> rltk.jaro_winkler_similarity('abchello', 'abcworld')
        0.6833333333333332
        >>> rltk.jaro_winkler_similarity('hello', 'world')
        0.4666666666666666
    """
    return 1 - _jaro_winkler(s1, s2, threshold, scaling_factor, prefix_len)


def jaro_distance(s1, s2):
    """
    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: Jaro Distance.

    Examples:
        >>> rltk.jaro_distance('abc', 'abd')
        0.7777777777777777
        >>> rltk.jaro_distance('abccd', 'abcdc')
        0.9333333333333332
    """
    return _jaro_distance(s1, s2)


def _jaro_distance(s1, s2):
    # code from https://github.com/nap/jaro-winkler-distance
    # Copyright Jean-Bernard Ratte

    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    shorter, longer = s1.lower(), s2.lower()

    if len(s1) > len(s2):
        longer, shorter = shorter, longer

    m1 = _get_matching_characters(shorter, longer)
    m2 = _get_matching_characters(longer, shorter)

    if len(m1) == 0 or len(m2) == 0:
        return 0.0

    return (float(len(m1)) / len(shorter) +
            float(len(m2)) / len(longer) +
            float(len(m1) - _transpositions(m1, m2)) / len(m1)) / 3.0


def _get_diff_index(first, second):
    if first == second:
        return -1

    if not first or not second:
        return 0

    max_len = min(len(first), len(second))
    for i in range(0, max_len):
        if not first[i] == second[i]:
            return i

    return max_len


def _get_prefix(first, second):
    if not first or not second:
        return ''

    index = _get_diff_index(first, second)
    if index == -1:
        return first
    elif index == 0:
        return ''
    else:
        return first[0:index]


def _get_matching_characters(first, second):
    common = []
    limit = math.floor(min(len(first), len(second)) / 2)

    for i, l in enumerate(first):
        left, right = int(max(0, i - limit)), int(min(i + limit + 1, len(second)))
        if l in second[left:right]:
            common.append(l)
            second = second[0:second.index(l)] + '*' + second[second.index(l) + 1:]

    return ''.join(common)


def _transpositions(first, second):
    return math.floor(len([(f, s) for f, s in zip(first, second) if not f == s]) / 2.0)
