import munkres
import rltk.utils as utils
from jaro import jaro_winkler_similarity

MIN_FLOAT = float('-inf')

cpdef double hybrid_jaccard_similarity(set1, set2, threshold=0.5, function=jaro_winkler_similarity, parameters={}):

    cdef double score_sum = 0.0
    cdef int matching_count = 0

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    matching_score = []
    for s1 in set1:
        inner = []
        for s2 in set2:
            score = function(s1, s2, **parameters)
            if score < threshold:
                score = 0.0
            inner.append(1.0 - score) # munkres finds out the smallest element
        matching_score.append(inner)

    indexes = munkres.Munkres().compute(matching_score)

    for r, c in indexes:
        matching_count += 1
        score_sum += 1.0 - matching_score[r][c]  # go back to similarity

    if len(set1) + len(set2) - matching_count == 0:
        return 1.0
    return score_sum / float(len(set1) + len(set2) - matching_count)


cpdef double monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters={}):

    cdef double score_num = 0.0
    cdef double max_score = 0.0

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

    return score_sum / float(len(bag1))


cpdef double symmetric_monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters={}):
    s1 = monge_elkan_similarity(bag1, bag2, function, parameters)
    s2 = monge_elkan_similarity(bag2, bag1, function, parameters)
    return (s1 + s2) / 2
