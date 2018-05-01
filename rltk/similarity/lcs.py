<<<<<<< HEAD
import rltk.utils as utils

=======
from collections import defaultdict

import rltk.utils as utils
>>>>>>> usc-isi-i2/master

def _lcs(s1, s2):
    m, n = len(s1), len(s2)

<<<<<<< HEAD
    dp = [[None] * (n + 1) for i in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0 or j == 0:
                dp[i][j] = 0
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


=======
    dp = [[None]*(n+1) for i in xrange(m+1)]

    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0 :
                dp[i][j] = 0
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]+1
            else:
                dp[i][j] = max(dp[i-1][j] , dp[i][j-1])

    return dp[m][n]

>>>>>>> usc-isi-i2/master
def longest_common_subsequence_distance(s1, s2):
    """
    The LCS distance between strings X (of length n) and Y (of length m) is n + m - 2 |LCS(X, Y)| min = 0 max = n + m

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: Longest Common Subsequence Distance.

    Examples:
        >>> rltk.longest_common_subsequence_distance('abcd', 'acbd')
        2
        >>> rltk.longest_common_subsequence_distance('abcdefg', 'acef')
        3
<<<<<<< HEAD
    """
    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    m, n = len(s1), len(s2)

    # dp = [[None] * (n + 1) for i in range(m + 1)]

    lcs = _lcs(s1, s2)
    return n + m - 2 * lcs

=======
    """ 
    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

    m, n = len(s1), len(s2)

    dp = [[None]*(n+1) for i in xrange(m+1)]

    lcs = _lcs(s1, s2)
    return n + m - 2*lcs
>>>>>>> usc-isi-i2/master

def metric_longest_common_subsequence(s1, s2):
    """
    The Metric LCS distance between 2 strings is similar to LCS between 2 string where Metric Longest Common Subsequence is computed as 1 - |LCS(s1, s2)| / max(|s1|, |s2|)

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: Metric Longest Common Subsequence Distance.

    Examples:
        >>> rltk.longest_common_subsequence('ABCDEFG', 'ABCDEFHJKL')
        0.4
        # LCS: ABCDEF => length = 6
        # longest = s2 => length = 10
        # => 1 - 6/10 = 0.4

        >>> rltk.optimal_string_alignment_distance('ABDEF', 'ABDIF')
        4
        # LCS: ABDF => length = 4
        # longest = ABDEF => length = 5
        # => 1 - 4 / 5 = 0.2
    """
    utils.check_for_none(s1, s2)
<<<<<<< HEAD
    utils.check_for_type(str, s1, s2)

    lcs = _lcs(s1, s2)
    return 1 - float(lcs) / max(len(s1), len(s2), 1)
=======
    utils.check_for_type(basestring, s1, s2)

    lcs = _lcs(s1, s2)
    return 1 - float(lcs)/max(len(s1),len(s2),1)
>>>>>>> usc-isi-i2/master
