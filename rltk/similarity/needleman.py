import rltk.utils as utils


def _get_score(c1, c2, match, mismatch, score_table):
    """
    if there's no score found in score_table, match & mismatch will be used.
    """
    if c1 in score_table and c2 in score_table[c1]:
        return score_table[c1][c2]
    else:
        return match if c1 == c2 else mismatch


def needleman_wunsch_score(s1, s2, match=2, mismatch=-1, gap=-0.5, score_table={}):
    utils.check_for_none(s1, s2)
    utils.check_for_type(str, s1, s2)

    # s1 = utils.unicode_normalize(s1)
    # s2 = utils.unicode_normalize(s2)

    n1, n2 = len(s1), len(s2)
    if n1 == 0 and n2 == 0:
        return 0

    # construct matrix to get max score of all possible alignments
    dp = [[0] * (n2 + 1) for _ in range(n1 + 1)]
    for i in range(n1 + 1):
        for j in range(n2 + 1):
            if i == 0 and j == 0:  # [0,0]
                continue
            elif i == 0:  # most top row
                dp[i][j] = gap + dp[i][j - 1]
            elif j == 0:  # most left column
                dp[i][j] = gap + dp[i - 1][j]
            else:
                dp[i][j] = max(dp[i][j - 1] + gap,
                               dp[i - 1][j] + gap,
                               dp[i - 1][j - 1] + _get_score(s1[i - 1], s2[j - 1], match, mismatch, score_table))

    return dp[n1][n2]


def needleman_wunsch_similarity(s1, s2, match=2, mismatch=-1, gap=-0.5, score_table={}):
    nm = needleman_wunsch_score(s1, s2, match, mismatch, gap, score_table)

    score_s1 = sum([_get_score(c1, c1, match, mismatch, score_table) for c1 in s1])
    score_s2 = sum([_get_score(c2, c2, match, mismatch, score_table) for c2 in s2])

    max_score = max(score_s1, score_s2)

    if max_score < nm:
        raise ValueError('Illegal value of score_table')

    return float(nm) / max_score
