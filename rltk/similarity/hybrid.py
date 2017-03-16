import utils
from jaro import jaro_winkler_similarity

MIN_FLOAT = float('-inf')

def hybrid_jaccard_similarity(set1, set2, threshold=0.5, function=jaro_winkler_similarity, parameters={}):

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    max_matching_dict = {s2: MIN_FLOAT for s2 in set2}

    for s1 in set1:
        for s2 in set2:
            score = function(s1, s2, **parameters)
            if score > threshold:
                max_matching_dict[s2] = max(max_matching_dict[s2], score)

    score_sum, matching_count = 0.0, 0
    for v in max_matching_dict.itervalues():
        matching_count += 1
        if v != MIN_FLOAT:
            score_sum += v

    if len(set1) + len(set2) - matching_count == 0:
        return 1.0
    return float(score_sum) / float(len(set1) + len(set2) - matching_count)


def monge_elkan_similarity(bag1, bag2, function=jaro_winkler_similarity, parameters={}):

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
