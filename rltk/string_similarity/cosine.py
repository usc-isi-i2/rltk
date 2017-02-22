import math
import utils

def _cosine(set1, set2):
    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return float(len(set1 & set2)) / (math.sqrt(float(len(set1))) * math.sqrt(float(len(set2))))

def cosine_similarity(set1, set2):
    return _cosine(set1, set2)

def cosine_distance(set1, set2):
    return 1 - cosine_similarity(set1, set2)

