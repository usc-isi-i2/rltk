import rltk.utils as utils

def _soundex(s):
    cdef int i = 0

    # utils.check_for_none(s)
    # utils.check_for_type(basestring, s)

    s = utils.unicode_normalize(s)

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
        ('AEIOUHWY', '.') # placeholder
    )
    CODE_DICT = dict((c, replace) for chars, replace in CODES for c in chars)

    sdx = s[0]
    for i in xrange(1, len(s)):
        if s[i] not in CODE_DICT:
            continue

        code = CODE_DICT[s[i]]
        if code == '.':
            continue
        if s[i] == s[i-1]: # ignore same letter
            continue
        if s[i-1] in CODE_DICT and CODE_DICT[s[i-1]] == code: # 'side-by-side' rule
            continue
        if s[i-1] in ('H', 'W') and i - 2 > 0 and\
                        s[i-2] in CODE_DICT and CODE_DICT[s[i-2]] != '.': # consonant separators
            continue

        sdx += code

    sdx = sdx[0:4].ljust(4, '0')

    return sdx

cpdef int soundex_similarity(s1, s2):
    return 1 if _soundex(s1) == _soundex(s2) else 0
