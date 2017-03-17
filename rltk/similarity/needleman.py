import utils

def needleman_wunsch_score(s1, s2, match=2, mismatch=-1, gap=-0.5, score_table={}):
    """
    if there's no score found in score_table, match & mismatch will be used.
    """
    def get_score(c1, c2):
        if c1 in score_table and c2 in score_table[c1]:
            return score_table[c1][c2]
        else:
            return match if c1 == c2 else mismatch

    utils.check_for_none(s1, s2)
    utils.check_for_type(basestring, s1, s2)

    s1 = utils.unicode_normalize(s1)
    s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    # construct matrix to get max score of all possible alignments
    dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
    for i in xrange(n1 + 1):
        for j in xrange(n2 + 1):
            if i == 0 and j == 0: # [0,0]
                continue
            elif i == 0: # most top row
                dp[i][j] = gap + dp[i][j-1]
            elif j == 0: # most left column
                dp[i][j] = gap + dp[i-1][j]
            else:
                dp[i][j] = max(dp[i][j-1] + gap,
                               dp[i-1][j] + gap,
                               dp[i-1][j-1] + get_score(s1[i-1], s2[j-1]))

    # # traceback to find alignment
    # i, j = n1, n2
    # a, b = '', ''
    # while i > 0 or j > 0:
    #     score = get_score(s1[i-1], s2[j-1])
    #     if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + score:
    #         a = s1[i-1] + a
    #         b = s2[j-1] + b
    #         i -= 1
    #         j -= 1
    #     elif i > 0 and dp[i][j] == dp[i-1][j] + gap:
    #         a = s1[i-1] + a
    #         b = '-' + b
    #         i -= 1
    #     else:
    #         a = '-' + a
    #         b = s2[j-1] + b
    #         j -= 1
    # print a, b

    return dp[n1][n2]

# in wiki:
# John- -Singer Sargent
# J-ane Klinger Sargent
# 28.5
# in lecture slide:
# John S-inger Sargent
# Jane Klinger Sargent
# 24.5
