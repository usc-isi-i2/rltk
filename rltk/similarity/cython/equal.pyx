import rltk.utils as utils


cpdef int string_equal(str1, str2):
    # utils.check_for_none(str1, str2)
    # utils.check_for_type(basestring, str1, str2)
    return int(str1 == str2)


cpdef int number_equal(int num1, int num2, epsilon=0):
    # utils.check_for_type((int, float), num1, num2)
    return int(abs(num1 - num2) <= epsilon)
