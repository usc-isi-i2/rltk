import munkres
import rltk.utils as utils
from rltk.similarity.jaro import jaro_winkler_similarity

MIN_FLOAT = float('-inf')


def hybrid_jaccard_similarity(set1, set2, threshold=0.5, function=jaro_winkler_similarity, parameters={}):
    """
    Generalized Jaccard Measure.

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.
        threshold (float, optional): The threshold to keep the score of similarity function. \
            Defaults to 0.5.
        function (function, optional): The reference of a similarity measure function. \
            It should return the value in range [0,1]. If it is set to None, \
            `jaro_winlker_similarity` will be used.
        parameters (dict, optional): Other parameters of function. Defaults to empty dict.

    Returns:
        float: Hybrid Jaccard similarity.

    Examples:
        >>> def hybrid_test_similarity(m ,n):
        ...     ...
        >>> rltk.hybrid_jaccard_similarity(set(['a','b','c']), set(['p', 'q']), function=hybrid_test_similarity)
        0.533333333333
    """

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    matching_score = []
    for s1 in set1:
        inner = []
        for s2 in set2:
            score = function(s1, s2, **parameters)
            if score < threshold:
                score = 0.0
            inner.append(1.0 - score)  # munkres finds out the smallest element
        matching_score.append(inner)

    indexes = munkres.Munkres().compute(matching_score)

    score_sum, matching_count = 0.0, 0
    for r, c in indexes:
        matching_count += 1
        score_sum += 1.0 - matching_score[r][c]  # go back to similarity

    if len(set1) + len(set2) - matching_count == 0:
        return 1.0
    return float(score_sum) / float(len(set1) + len(set2) - matching_count)


def monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters={}):
    """
    Monge Elkan similarity.

    Args:
        bag1 (list): Bag 1.
        bag2 (list): Bag 2.
        function (function, optional): The reference of a similarity measure function. \
            It should return the value in range [0,1]. If it is set to None, \
            `jaro_winlker_similarity` will be used.
        parameters (dict, optional): Other parameters of function. Defaults to empty dict.

    Returns:
        float: Monge Elkan similarity.
    """

    utils.check_for_none(bag1, bag2)
    utils.check_for_type(list, bag1, bag2)

    if len(bag1) == 0:
        return 0.0

    score_sum = 0
    for ele1 in bag1:
        max_score = MIN_FLOAT
        for ele2 in bag2:
            max_score = max(max_score, function(ele1, ele2, **parameters))
        score_sum += max_score

    return float(score_sum) / float(len(bag1))


def symmetric_monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters={}):
    """
    Symmetric Monge Elkan similarity is computed by \
    (monge_elkan_similarity(b1, b2) + monge_elkan_similarity(b2, b1)) / 2.
    """

    s1 = monge_elkan_similarity(bag1, bag2, function, parameters)
    s2 = monge_elkan_similarity(bag2, bag1, function, parameters)
    return (s1 + s2) / 2
