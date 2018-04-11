import rltk.utils as utils


def soundex(s):
    """
    The standard used for this implementation is provided by `U.S. Census Bureau <https://www.archives.gov/research/census/soundex.html>`_.

    Args:
        s (str): Sequence.

    Returns:
        str: Coded sequence.

    Examples:
        >>> rltk.soundex('ashcraft')
        'A261'
        >>> rltk.soundex('pineapple')
        'P514'
    """

    utils.check_for_none(s)
    utils.check_for_type(str, s)

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
        ('AEIOUHWY', '.')  # placeholder
    )
    CODE_DICT = dict((c, replace) for chars, replace in CODES for c in chars)

    sdx = s[0]
    for i in range(1, len(s)):
        if s[i] not in CODE_DICT:
            continue

        code = CODE_DICT[s[i]]
        if code == '.':
            continue
        if s[i] == s[i - 1]:  # ignore same letter
            continue
        if s[i - 1] in CODE_DICT and CODE_DICT[s[i - 1]] == code:  # 'side-by-side' rule
            continue
        if s[i - 1] in ('H', 'W') and i - 2 > 0 and \
                        s[i - 2] in CODE_DICT and CODE_DICT[s[i - 2]] != '.':  # consonant separators
            continue

        sdx += code

    sdx = sdx[0:4].ljust(4, '0')

    return sdx


def soundex_similarity(s1, s2):
    """
    soundex(s1) == soundex(s2)
    
    Args:
        s1 (str): Sequence.
        s2 (str): Sequence.

    Returns:
        float: if soundex(s1) equals to soundex(s2)
    """
    return 1 if soundex(s1) == soundex(s2) else 0
