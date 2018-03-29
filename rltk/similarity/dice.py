import rltk.utils as utils


def dice_similarity(set1, set2):
    """
    The Dice similarity score is defined as twice the intersection of two sets divided by sum of lengths.

    Args:
        set1 (set): Set 1.
        set2 (set): Set 2.

    Returns:
        float: Dice similarity.

    Examples:
        >>> rltk.dice_similarity(set(['a', 'b']), set(['c', 'b']))
        0.5
    """

    utils.check_for_none(set1, set2)
    utils.check_for_type(set, set1, set2)

    if len(set1) == 0 or len(set2) == 0:
        return 0

    return 2.0 * float(len(set1 & set2)) / float(len(set1) + len(set2))
