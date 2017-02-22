from collections import defaultdict

import utils

def _levenshtein(s1, s2):
    """
    code modifed from niR@github https://github.com/pupuhime
    time: O(n1*n2)
    space: O(n1*n2)
    """

    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    if n1 == 0 or n2 == 0:
        return max(n1, n2)

    lev_matrix = [[0 for i1 in range(n1 + 1)] for i2 in range(n2 + 1)]
    for i1 in range(1, n1 + 1):
        lev_matrix[0][i1] = i1
    for i2 in range(1, n2 + 1):
        lev_matrix[i2][0] = i2
    for i2 in range(1, n2 + 1):
        for i1 in range(1, n1 + 1):
            cost = 0 if s1[i1 - 1] == s2[i2 - 1] else 1
            elem = min(lev_matrix[i2 - 1][i1] + 1,
                       lev_matrix[i2][i1 - 1] + 1,
                       lev_matrix[i2 - 1][i1 - 1] + cost)
            lev_matrix[i2][i1] = elem
    return lev_matrix[-1][-1]

def levenshtein_similarity(s1, s2):
    lev = _levenshtein(s1, s2)
    return 1 - float(lev) / max(len(s1), len(s2)) if lev != 0 else 1

def levenshtein_distance(s1, s2):
    return _levenshtein(s1, s2)


def _normalized_levenshtein(s1, s2):
    lev = _levenshtein(s1, s2)

    n1, n2 = len(s1), len(s2)
    max_len = max(n1, n2)
    if max_len == 0:
        return 0

    return float(lev) / max_len

def normalized_levenshtein_similarity(s1, s2):
    return 1 - normalized_levenshtein_distance(s1, s2)

def normalized_levenshtein_distance(s1, s2):
    return _normalized_levenshtein(s1, s2)

def damerau_levenshtein_distance(s1, s2):
    """
    code modified from https://github.com/jamesturk/jellyfish
    """

    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    infinite = n1 + n2

    # character array
    da = defaultdict(int)

    # distance matrix
    score = [[0] * (n2 + 2) for x in xrange(n1 + 2)]

    score[0][0] = infinite
    for i in xrange(0, n1 + 1):
        score[i + 1][0] = infinite
        score[i + 1][1] = i
    for i in xrange(0, n2 + 1):
        score[0][i + 1] = infinite
        score[1][i + 1] = i

    for i in xrange(1, n1 + 1):
        db = 0
        for j in xrange(1, n2 + 1):
            i1 = da[s2[j - 1]]
            j1 = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j

            score[i + 1][j + 1] = min(score[i][j] + cost,
                                      score[i + 1][j] + 1,
                                      score[i][j + 1] + 1,
                                      score[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1))
        da[s1[i - 1]] = i

    return score[n1 + 1][n2 + 1]
