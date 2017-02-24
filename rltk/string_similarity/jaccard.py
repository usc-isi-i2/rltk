import utils

def _jaccard_index(set1, set2):
    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return float(len(set1 & set2)) / float(len(set1 | set2))

def jaccard_index_similarity(set1, set2):
    """
    The Jaccard Index Similarity is then computed as intersection(set1, set2) / union(set1, set2).

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.

    Returns:
        float: Jaccard Index similarity.

    Examples:
        >>> rltk.jaccard_index_similarity(set(['a','b']), set(['a','c']))
        0.3333333333333333
        >>> rltk.jaccard_index_similarity(set(['a','b']), set(['c','d']))
        0.0
    """
    return _jaccard_index(set1, set2)

def jaccard_index_distance(set1, set2):
    """
    The Jaccard Index Distance is then computed as 1 - jaccard_index_similarity.

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.

    Returns:
        int: Jaccard Index Distance.
    """
    return 1 - jaccard_index_similarity(set1, set2)

