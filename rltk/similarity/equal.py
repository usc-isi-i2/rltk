import rltk.utils as utils


def string_equal(str1, str2):
    """
    Args:
        n1 (str): String 1.
        n2 (str): String 2.

    Returns:
        int: 0 for unequal and 1 for equal.
    """

    utils.check_for_none(str1, str2)
    utils.check_for_type(str, str1, str2)
    return int(str1 == str2)


def number_equal(num1, num2, epsilon=0):
    """
    Args:
        n1 (int / float): Number 1.
        n2 (int / float): Number 2.
        epsilon (float, optional): Approximation margin.

    Returns:
        int: 0 for unequal and 1 for equal.
    """

    utils.check_for_type((int, float), num1, num2)
    return int(abs(num1 - num2) <= epsilon)
