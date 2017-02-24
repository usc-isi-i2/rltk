from collections import defaultdict

import utils

def _levenshtein(s1, s2, insert, delete, substitute,
                 insert_default, delete_default, substitute_default):
    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    # if n1 == 0 or n2 == 0:
    #     return max(n1, n2)

    dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
    for i in xrange(n1 + 1):
        for j in xrange(n2 + 1):
            if i == 0 and j == 0: # [0,0]
                continue
            if i == 0: # most top row
                c = s2[j-1]
                dp[i][j] = insert[c] if c in insert else insert_default
                dp[i][j] += dp[i][j-1]
            elif j == 0: # most left column
                c = s1[i-1]
                dp[i][j] = delete[c] if c in delete else delete_default
                dp[i][j] += dp[i-1][j]
            else:
                c1, c2 = s1[i-1], s2[j-1]
                insert_cost = insert[c2] if c2 in insert else insert_default
                delete_cost = delete[c1] if c1 in delete else delete_default
                substitute_cost = substitute[c1][c2] \
                    if c1 in substitute and c2 in substitute[c1] else substitute_default

                if c1 == c2:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i][j-1] + insert_cost,
                                   dp[i-1][j] + delete_cost,
                                   dp[i-1][j-1] + substitute_cost)
    return dp[n1][n2]

def levenshtein_similarity(s1, s2, insert={}, delete={}, substitute={},
                           insert_default=1, delete_default=1, substitute_default=1):
    """
    The Levenshtein similarity is computed as 1 - levenshtein_distance / max(len(s1), len(s2))

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.
        insert (dict(str, int)): Insert cost of characters. Defaults to empty dict.
        delete (dict(str, int)): Delete cost of characters. Defaults to empty dict.
        substitute (dict(str, dict(str, int)), optional): Substitute cost of characters. Defaults to empty dict.
        insert_default (int, optional): Default value of insert cost. Defaults to 1.
        delete_default (int, optional): Default value of delete cost. Defaults to 1.
        substitute_default (int, optional): Default value of substitute cost. Defaults to 1.

    Returns:
        int: Levenshtein similarity.
    """

    lev = _levenshtein(s1, s2, insert, delete, substitute,
                           insert_default, delete_default, substitute_default)
    return 1 - float(lev) / max(len(s1), len(s2)) if lev != 0 else 1

def levenshtein_distance(s1, s2, insert={}, delete={}, substitute={},
                           insert_default=1, delete_default=1, substitute_default=1):
    """
    The Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.
        insert (dict(str, int)): Insert cost of characters. Defaults to empty dict.
        delete (dict(str, int)): Delete cost of characters. Defaults to empty dict.
        substitute (dict(str, dict(str, int)), optional): Substitute cost of characters. Defaults to empty dict.
        insert_default (int, optional): Default value of insert cost. Defaults to 1.
        delete_default (int, optional): Default value of delete cost. Defaults to 1.
        substitute_default (int, optional): Default value of substitute cost. Defaults to 1.

    Returns:
        int: Levenshtein distance.

    Examples:
        >>> rltk.levenshtein_distance('ab', 'abc')
        1
        >>> rltk.levenshtein_distance('a', 'abc', insert = {'c':50},
        ... insert_default=100, delete_default=100, substitute_default=100)
        150
    """

    return _levenshtein(s1, s2, insert, delete, substitute,
                           insert_default, delete_default, substitute_default)


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
    # code modified from https://github.com/jamesturk/jellyfish

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
