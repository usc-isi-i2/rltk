import rltk.utils as utils


def string_equal(str1, str2):
    utils.check_for_none(str1, str2)
    utils.check_for_type(str, str1, str2)
    return int(str1 == str2)


def number_equal(num1, num2, epsilon=0):
    utils.check_for_type((int, float), num1, num2)
    return int(abs(num1 - num2) <= epsilon)
