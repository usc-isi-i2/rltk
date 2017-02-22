import utils

def _levenshtein(s1, s2):
    def helper(str1, n1, str2, n2):
        """
        code from niR@github https://github.com/pupuhime
        time: O(n1*n2)
        space: O(n1*n2)
        """
        lev_matrix = [[0 for i1 in range(n1 + 1)] for i2 in range(n2 + 1)]
        for i1 in range(1, n1 + 1):
            lev_matrix[0][i1] = i1
        for i2 in range(1, n2 + 1):
            lev_matrix[i2][0] = i2
        for i2 in range(1, n2 + 1):
            for i1 in range(1, n1 + 1):
                cost = 0 if str1[i1 - 1] == str2[i2 - 1] else 1
                elem = min(lev_matrix[i2 - 1][i1] + 1,
                           lev_matrix[i2][i1 - 1] + 1,
                           lev_matrix[i2 - 1][i1 - 1] + cost)
                lev_matrix[i2][i1] = elem
        return lev_matrix[-1][-1]

    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    if n1 == 0 or n2 == 0:
        return max(n1, n2)

    return helper(s1, n1, s2, n2)

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
