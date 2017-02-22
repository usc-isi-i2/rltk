import utils

def _jaccard_index(set1, set2):
    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return float(len(set1 & set2)) / float(len(set1 | set2))

def jaccard_index_similarity(set1, set2):
    return _jaccard_index(set1, set2)

def jaccard_index_distance(set1, set2):
    return 1 - jaccard_index_similarity(set1, set2)

