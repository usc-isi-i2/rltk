import unicodedata

import utils

def soundex(s):

    utils.check_for_none(s)
    utils.check_for_type(basestring, s)

    if isinstance(s, unicode):
        s = unicodedata.normalize('NFKD', s)

    if len(s) == 0:
        raise ValueError('Empty string')

    s = s.upper()

    CODES = (
        ('BFPV', '1'),
        ('CGJKQSXZ', '2'),
        ('DT', '3'),
        ('L', '4'),
        ('MN', '5'),
        ('R', '6'),
        ('AEIOUHWY', '.')
    )
    CODE_DICT = dict((c, replace) for chars, replace in CODES for c in chars)

    sdx = s[0]
    for c in s[1:]:
        if c in CODE_DICT:
            code = CODE_DICT[c]
            if code != sdx[-1]:
                sdx += code

    sdx = sdx.replace('.', '')
    sdx = sdx[0:4].ljust(4, '0')

    return sdx

def soundex_us(s):
    """
    U.S. Census soundex
    """
    pass