import rltk.utils as utils


def ngram_distance(s0, s1, n=2):
    """
    N-Gram Distance as defined by Kondrak, "N-Gram Similarity and Distance" String Processing and Information Retrieval, Lecture Notes in Computer Science Volume 3772, 2005, pp 115-126.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: NGram Distance.

    Examples:
        >>> rltk.ngram_distance('ABCD', 'ABTUIO')
        0.5833
    """

    utils.check_for_none(s0, s1)
    utils.check_for_type(str, s0, s1)

    n1, n2 = len(s0), len(s1)
    special = "\n"

    if (n1 == 0 or n2 == 0):
        return 1

    if (s0 == s1):
        return 0

    cost = 0
    if (n1 < n or n2 < n):
        return 1

    # Adding special chars (n-1) to s0
    sa = special * (n - 1) + s0

    s2_j = [None] * n  # jth n-gram of s2
    d = [0] * (n1 + 1)  # cost array, horizontally
    p = [0] * (n1 + 1)  # 'previous' cost array, horizontally

    for i in range(n1 + 1):
        p[i] = i

    for j in range(1, n2 + 1):
        # Construct s2_j n-gram
        if (j < n):
            for ti in range(n - j):
                s2_j[ti] = special

            for ti in range(n - j, n):
                s2_j[ti] = s1[ti - (n - j)]

        else:
            s2_j = list(s1[j - n: j])

        d[0] = j

        for i in range(1, n1 + 1):
            cost = 0
            tn = n
            # Compare sa to s2_j
            for ni in range(n):
                if sa[i - 1 + ni] != s2_j[ni]:
                    cost += 1
                elif sa[i - 1 + ni] == special:
                    tn -= 1

            ec = float(cost) / tn
            # minimum of cell to the left+1, to the top+1,
            # diagonally left and up +cost
            d[i] = min(d[i - 1] + 1, p[i] + 1, p[i - 1] + ec)

        d2 = p
        p = d
        d = d2
    return float(p[n1]) / max(n2, n1)


def ngram_similarity(s0, s1, n=2):
    """
    N-Gram Similarity as defined by Kondrak, "N-Gram Similarity and Distance" String Processing and Information Retrieval, Lecture Notes in Computer Science Volume 3772, 2005, pp 115-126.

    Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: NGram Similarity.

    Examples:
        >>> rltk.ngram_similarity('ABCD', 'ABTUIO')
        0.4166666666666667
    """

    utils.check_for_none(s0, s1)
    utils.check_for_type(str, s0, s1)

    n1, n2 = len(s0), len(s1)
    special = "\n"

    if (n1 == 0 or n2 == 0):
        return 0

    if (s0 == s1):
        return 1

    cost = 0
    if (n1 < n or n2 < n):
        return 0

    # Adding special chars (n-1) to s0
    sa = special * (n - 1) + s0

    s2_j = [None] * n  # jth n-gram of s2
    d = [0] * (n1 + 1)  # cost array, horizontally
    p = [0] * (n1 + 1)  # 'previous' cost array, horizontally

    for i in range(n1 + 1):
        p[i] = 0

    for j in range(1, n2 + 1):
        # Construct s2_j n-gram
        if (j < n):
            for ti in range(n - j):
                s2_j[ti] = special

            for ti in range(n - j, n):
                s2_j[ti] = s1[ti - (n - j)]

        else:
            s2_j = list(s1[j - n: j])

        d[0] = 0

        for i in range(1, n1 + 1):
            cost = 0
            tn = n
            # Compare sa to s2_j
            for ni in range(n):
                if sa[i - 1 + ni] == s2_j[ni] and sa[i - 1 + ni] != "\n":
                    cost += 1
                elif sa[i - 1 + ni] == special:
                    tn -= 1

            ec = float(cost) / tn
            # minimum of cell to the left+1, to the top+1,
            # diagonally left and up +cost
            d[i] = max(d[i - 1], p[i], p[i - 1] + ec)

        d2 = p
        p = d
        d = d2
    return float(p[n1]) / max(n2, n1)
