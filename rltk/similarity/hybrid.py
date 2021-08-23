from scipy.optimize import linear_sum_assignment
import rltk.utils as utils
from rltk.similarity.jaro import jaro_winkler_similarity

MIN_FLOAT = float('-inf')


def hybrid_jaccard_similarity(set1, set2, threshold=0.5, function=jaro_winkler_similarity,
                              parameters=None, lower_bound=None):
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
        parameters (dict, optional): Other parameters of function. Defaults to None.
        lower_bound (float): This is for early exit. If the similarity is not possible to satisfy this value, \
            the function returns immediately with the return value 0.0. Defaults to None.

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

    parameters = parameters if isinstance(parameters, dict) else {}

    if len(set1) > len(set2):
        set1, set2 = set2, set1
    total_num_matches = len(set1)

    matching_score = [[1.0] * len(set2) for _ in range(len(set1))]
    row_max = [0.0] * len(set1)
    for i, s1 in enumerate(set1):
        for j, s2 in enumerate(set2):
            score = function(s1, s2, **parameters)
            if score < threshold:
                score = 0.0
            row_max[i] = max(row_max[i], score)
            matching_score[i][j] = 1.0 - score  # munkres finds out the smallest element

        if lower_bound:
            max_possible_score_sum = sum(row_max[:i+1] + [1] * (total_num_matches - i - 1))
            max_possible = 1.0 * max_possible_score_sum / float(len(set1) + len(set2) - total_num_matches)
            if max_possible < lower_bound:
                return 0.0

    # run munkres, finds the min score (max similarity) for each row
    row_idx, col_idx = linear_sum_assignment(matching_score)

    # recover scores
    score_sum = 0.0
    for r, c in zip(row_idx, col_idx):
        score_sum += 1.0 - matching_score[r][c]

    if len(set1) + len(set2) - total_num_matches == 0:
        return 1.0
    return float(score_sum) / float(len(set1) + len(set2) - total_num_matches)


def monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters=None, lower_bound=None):
    """
    Monge Elkan similarity.

    Args:
        bag1 (list): Bag 1.
        bag2 (list): Bag 2.
        function (function, optional): The reference of a similarity measure function. \
            It should return the value in range [0,1]. If it is set to None, \
            `jaro_winlker_similarity` will be used.
        parameters (dict, optional): Other parameters of function. Defaults to None.
        lower_bound (float): This is for early exit. If the similarity is not possible to satisfy this value, \
            the function returns immediately with the return value 0.0. Defaults to None.

    Returns:
        float: Monge Elkan similarity.

    Note:
        The order of bag1 and bag2 matters. \
            Alternatively, `symmetric_monge_elkan_similarity` is not sensitive to the order.
        If the `lower_bound` is set, the early exit condition is more easy to be triggered if bag1 has bigger size.
    """

    utils.check_for_none(bag1, bag2)
    utils.check_for_type(list, bag1, bag2)

    parameters = parameters if isinstance(parameters, dict) else {}

    score_sum = 0
    for idx, ele1 in enumerate(bag1):
        max_score = MIN_FLOAT
        for ele2 in bag2:
            max_score = max(max_score, function(ele1, ele2, **parameters))
        score_sum += max_score

        # if it satisfies early exit condition
        if lower_bound:
            rest_max = len(bag1) - 1 - idx  # assume the rest scores are all 1
            if float(score_sum + rest_max) / float(len(bag1)) < lower_bound:
                return 0.0

    return float(score_sum) / float(len(bag1))


def symmetric_monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters=None):
    """
    Symmetric Monge Elkan similarity is computed by \
    (monge_elkan_similarity(b1, b2) + monge_elkan_similarity(b2, b1)) / 2.
    """

    s1 = monge_elkan_similarity(bag1, bag2, function, parameters)
    s2 = monge_elkan_similarity(bag2, bag1, function, parameters)
    return (s1 + s2) / 2
