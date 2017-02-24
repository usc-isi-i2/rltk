import utils

def nysiis(s):
    """
    New York State Immunization Information System (NYSIIS) Phonetic Code is a phonetic algorithm created by `The New York State Department of Health's (NYSDOH) Bureau of Immunization
    <https://www.health.ny.gov/prevention/immunization/information_system/>`_.

    Args:
        s (str): Sequence.

    Returns:
        str: Coded sequence.

    Examples:
        >>> rltk.metaphone('ashcraft')
        'AXKRFT'
        >>> rltk.metaphone('pineapple')
        'PNPL'
    """
    # code from https://github.com/jamesturk/jellyfish

    utils.check_for_none(s)
    utils.check_for_type(basestring, s)

    s = utils.unicode_normalize(s)

    if len(s) == 0:
        raise ValueError('Empty string')

    s = s.upper()
    key = []

    # step 1 - prefixes
    if s.startswith('MAC'):
        s = 'MCC' + s[3:]
    elif s.startswith('KN'):
        s = s[1:]
    elif s.startswith('K'):
        s = 'C' + s[1:]
    elif s.startswith(('PH', 'PF')):
        s = 'FF' + s[2:]
    elif s.startswith('SCH'):
        s = 'SSS' + s[3:]

    # step 2 - suffixes
    if s.endswith(('IE', 'EE')):
        s = s[:-2] + 'Y'
    elif s.endswith(('DT', 'RT', 'RD', 'NT', 'ND')):
        s = s[:-2] + 'D'

    # step 3 - first character of key comes from name
    key.append(s[0])

    # step 4 - translate remaining chars
    i = 1
    len_s = len(s)
    while i < len_s:
        ch = s[i]
        if ch == 'E' and i+1 < len_s and s[i+1] == 'V':
            ch = 'AF'
            i += 1
        elif ch in 'AEIOU':
            ch = 'A'
        elif ch == 'Q':
            ch = 'G'
        elif ch == 'Z':
            ch = 'S'
        elif ch == 'M':
            ch = 'N'
        elif ch == 'K':
            if i+1 < len(s) and s[i+1] == 'N':
                ch = 'N'
            else:
                ch = 'C'
        elif ch == 'S' and s[i+1:i+3] == 'CH':
            ch = 'SS'
            i += 2
        elif ch == 'P' and i+1 < len(s) and s[i+1] == 'H':
            ch = 'F'
            i += 1
        elif ch == 'H' and (s[i-1] not in 'AEIOU' or (i+1 < len(s) and s[i+1] not in 'AEIOU')):
            if s[i-1] in 'AEIOU':
                ch = 'A'
            else:
                ch = s[i-1]
        elif ch == 'W' and s[i-1] in 'AEIOU':
            ch = s[i-1]

        if ch[-1] != key[-1][-1]:
            key.append(ch)

        i += 1

    key = ''.join(key)

    # step 5 - remove trailing S
    if key.endswith('S') and key != 'S':
        key = key[:-1]

    # step 6 - replace AY w/ Y
    if key.endswith('AY'):
        key = key[:-2] + 'Y'

    # step 7 - remove trailing A
    if key.endswith('A') and key != 'A':
        key = key[:-1]

    # step 8 was already done

    return key
