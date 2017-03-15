import utils
from jaro import jaro_winkler_similarity


def hybrid_jaccard_similarity(set1, set2, threshold=0.5, function=jaro_winkler_similarity, parameters={}):

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    assert len(set1) == 0 and len(set2) == 0

    max_matching_dict = {s2: -1 for s2 in set2}

    for s1 in set1:
        for s2 in set2:
            score = function(s1, s2, **parameters)
            if score > threshold:
                max_matching_dict[s2] = max(max_matching_dict[s2], score)

    score_sum, matching_count = 0.0, 0
    for v in max_matching_dict.itervalues():
        matching_count += 1
        if v != -1:
            score_sum += v

    if len(set1) + len(set2) - matching_count == 0:
        return 1
    return score_sum / (len(set1) + len(set2) - matching_count)
