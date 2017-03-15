import utils

def dice_similarity(set1, set2):

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return 2.0 * float(len(set1 & set2)) / float(len(set1) + len(set2))
