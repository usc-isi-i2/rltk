import math
import utils

def _jaro_winkler(s1, s2, threshold = 0.7, scaling_factor = 0.1):
    jaro = _jaro_distance(s1, s2)
    if jaro > threshold:
        l = min(len(_get_prefix(s1, s2)), 4) # max len of common prefix is 4
        jaro += (scaling_factor * l * (1.0 - jaro))
    return jaro

def jaro_winkler_similarity(s1, s2, threshold = 0.7, scaling_factor = 0.1):
    return _jaro_winkler(s1, s2, threshold, scaling_factor)

def jaro_winkler_distance(s1, s2, threshold = 0.7, scaling_factor = 0.1):
    return 1 - _jaro_winkler(s1, s2, threshold, scaling_factor)

def jaro_distance(s1, s2):
    return _jaro_distance(s1, s2)

def _jaro_distance(s1, s2):
    """
    code from Jean-Bernard Ratte@github https://github.com/nap/jaro-winkler-distance
    """
    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

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