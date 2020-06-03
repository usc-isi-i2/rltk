from collections import defaultdict

import rltk.utils as utils


def levenshtein_distance(s1, s2, insert=None, delete=None, substitute=None,
                         insert_default=1, delete_default=1, substitute_default=1):
    """
    The Levenshtein distance between two words is the minimum number of single-character edits (insertions, \
    deletions or substitutions) required to change one word into the other.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.
        insert (dict(str, int), optional): Insert cost of characters. Defaults to None.
        delete (dict(str, int), optional): Delete cost of characters. Defaults to None.
        substitute (dict(str, dict(str, int)), optional): Substitute cost of characters. Defaults to None.
        insert_default (int, optional): Default value of insert cost. Defaults to 1.
        delete_default (int, optional): Default value of delete cost. Defaults to 1.
        substitute_default (int, optional): Default value of substitute cost. Defaults to 1.

    Returns:
        int: Levenshtein Distance.

    Examples:
        >>> rltk.levenshtein_distance('ab', 'abc')
        1
        >>> rltk.levenshtein_distance('a', 'abc', insert = {'c':50},
        ... insert_default=100, delete_default=100, substitute_default=100)
        150
    """

    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    insert = insert if isinstance(insert, dict) else {}
    delete = delete if isinstance(delete, dict) else {}
    substitute = substitute if isinstance(substitute, dict) else {}

    # s1 = utils.unicode_normalize(s1)
    # s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    # if n1 == 0 or n2 == 0:
    #     return max(n1, n2)

    dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
    for i in range(n1 + 1):
        for j in range(n2 + 1):
            if i == 0 and j == 0:  # [0,0]
                continue
            elif i == 0:  # most top row
                c = s2[j - 1]
                dp[i][j] = insert[c] if c in insert else insert_default
                dp[i][j] += dp[i][j - 1]
            elif j == 0:  # most left column
                c = s1[i - 1]
                dp[i][j] = delete[c] if c in delete else delete_default
                dp[i][j] += dp[i - 1][j]
            else:
                c1, c2 = s1[i - 1], s2[j - 1]
                insert_cost = insert[c2] if c2 in insert else insert_default
                delete_cost = delete[c1] if c1 in delete else delete_default
                substitute_cost = substitute[c1][c2] \
                    if c1 in substitute and c2 in substitute[c1] else substitute_default

                if c1 == c2:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i][j - 1] + insert_cost,
                                   dp[i - 1][j] + delete_cost,
                                   dp[i - 1][j - 1] + substitute_cost)
    return dp[n1][n2]


def levenshtein_similarity(s1, s2, insert=None, delete=None, substitute=None,
                                    insert_default=1, delete_default=1, substitute_default=1):
    """
    Computed as 1 - levenshtein_distance / max-cost(s1,s2)
    """
    insert = insert if isinstance(insert, dict) else {}
    delete = delete if isinstance(delete, dict) else {}
    substitute = substitute if isinstance(substitute, dict) else {}

    def compute_max_cost(s):
        return sum([
            max(
                insert[c] if c in insert else insert_default,
                delete[c] if c in delete else delete_default,
                substitute[c] if c in substitute else substitute_default
            ) for c in s
        ])

    lev = levenshtein_distance(s1, s2, insert, delete, substitute,
                               insert_default, delete_default, substitute_default)

    max_cost = max(compute_max_cost(s1), compute_max_cost(s2))

    if max_cost < lev:
        raise ValueError('Illegal value of operation cost')

    if max_cost == 0:
        return 1.0

    return 1.0 - float(lev) / max_cost


def damerau_levenshtein_distance(s1, s2):
    """
    Similar to Levenshtein, Damerau-Levenshtein distance is the minimum number of operations needed to transform\
     one string into the other, where an operation is defined as an insertion, deletion, or substitution of \
     a single character, or a transposition of two adjacent characters.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: Damerau Levenshtein Distance.

    Examples:
        >>> rltk.damerau_levenshtein_distance('abcd', 'acbd')
        1
        >>> rltk.damerau_levenshtein_distance('abbd', 'acad')
        2
    """

    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    # s1 = utils.unicode_normalize(s1)
    # s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    infinite = n1 + n2

    char_arr = defaultdict(int)
    dp = [[0] * (n2 + 2) for _ in range(n1 + 2)]

    dp[0][0] = infinite
    for i in range(0, n1 + 1):
        dp[i + 1][0] = infinite
        dp[i + 1][1] = i
    for i in range(0, n2 + 1):
        dp[0][i + 1] = infinite
        dp[1][i + 1] = i

    for i in range(1, n1 + 1):
        db = 0
        for j in range(1, n2 + 1):
            i1 = char_arr[s2[j - 1]]
            j1 = db
            cost = 1
            if s1[i - 1] == s2[j - 1]:
                cost = 0
                db = j

            dp[i + 1][j + 1] = min(dp[i][j] + cost,
                                   dp[i + 1][j] + 1,
                                   dp[i][j + 1] + 1,
                                   dp[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1))
        char_arr[s1[i - 1]] = i

    return dp[n1 + 1][n2 + 1]


def damerau_levenshtein_similarity(s1, s2):
    """
    Computed as 1 - damerau_levenshtein_distance / max(len(s1), len(s2))
    """
    max_cost = max(len(s1), len(s2))

    if max_cost == 0:
        return 1.0

    return 1.0 - float(damerau_levenshtein_distance(s1, s2)) / max_cost


def optimal_string_alignment_distance(s1, s2):
        """
        This is a variation of the Damerau-Levenshtein distance that returns the strings' edit distance
        taking into account deletion, insertion, substitution, and transposition, under the condition
        that no substring is edited more than once.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Optimal String Alignment Distance.

        Examples:
            >>> rltk.optimal_string_alignment_distance('abcd', 'acbd')
            1
            >>> rltk.optimal_string_alignment_distance('ca', 'abc')
            3
        """

        utils.check_for_none(s1, s2)
        utils.check_for_type(str, s1, s2)

        # s1 = utils.unicode_normalize(s1)
        # s2 = utils.unicode_normalize(s2)

        n1, n2 = len(s1), len(s2)

        dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]

        for i in range(0, n1 + 1):
            dp[i][0] = i
        for j in range(0, n2 + 1):
            dp[0][j] = j

        for i in range(1, n1 + 1):
            for j in range(1, n2 + 1):
                cost = 0 if s1[i - 1] == s2[j - 1] else 1

                dp[i][j] = min(dp[i][j - 1] + 1,
                               dp[i - 1][j] + 1,
                               dp[i - 1][j - 1] + cost)

                if i > 1 and j > 1 and s1[i - 1] == s2[j - 2] and s1[i - 2] == s2[j - 1]:
                    dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + cost)

        return dp[n1][n2]


def optimal_string_alignment_similarity(s1, s2):
    """
    Computed as 1 - optimal_string_alignment_distance / max(len(s1), len(s2))
    """
    max_cost = max(len(s1), len(s2))

    if max_cost == 0:
        return 1.0

    return 1.0 - float(optimal_string_alignment_distance(s1, s2)) / max_cost
