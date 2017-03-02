import math
import utils

def _cosine(set1, set2):
    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return float(len(set1 & set2)) / (math.sqrt(float(len(set1))) * math.sqrt(float(len(set2))))

def cosine_similarity(set1, set2):
    """
    The similarity between the two strings is the cosine of the angle between these two vectors representation.

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.

    Returns:
        float: Consine similarity in range [0.0, 1.0].

    Examples:
        >>> rltk.cosine_similarity(set([1,2]), set([3,4]))
        0.0
        >>> rltk.cosine_similarity(set([1,2]), set([2,3]))
        0.5
        >>> rltk.cosine_similarity(set([1,2]), set([1,2]))
        1.0
    """
    return _cosine(set1, set2)

def cosine_distance(set1, set2):
    """
    Distance of Cosine similarity is computed as 1 - cosine_similarity.

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.

    Returns:
        int: Distance of Consine similarity.
    """
    return 1 - cosine_similarity(set1, set2)

