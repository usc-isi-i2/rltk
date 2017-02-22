import unicodedata

import utils

def metaphone(s):
    """
    code from https://github.com/jamesturk/jellyfish
    """
    utils.check_for_none(s)
    utils.check_for_type(basestring, s)

    if isinstance(s, unicode):
        s = unicodedata.normalize('NFKD', s)

    if len(s) == 0:
        raise ValueError('Empty string')

    s = s.lower()
    result = []

    # skip first character if s starts with these
    if s.startswith(('kn', 'gn', 'pn', 'ac', 'wr', 'ae')):
        s = s[1:]

    i = 0

    while i < len(s):
        c = s[i]
        next = s[i+1] if i < len(s)-1 else '*****'
        nextnext = s[i+2] if i < len(s)-2 else '*****'

        # skip doubles except for cc
        if c == next and c != 'c':
            i += 1
            continue

        if c in 'aeiou':
            if i == 0 or s[i-1] == ' ':
                result.append(c)
        elif c == 'b':
            if (not (i != 0 and s[i-1] == 'm')) or next:
                result.append('b')
        elif c == 'c':
            if next == 'i' and nextnext == 'a' or next == 'h':
                result.append('x')
                i += 1
            elif next in 'iey':
                result.append('s')
                i += 1
            else:
                result.append('k')
        elif c == 'd':
            if next == 'g' and nextnext in 'iey':
                result.append('j')
                i += 2
            else:
                result.append('t')
        elif c in 'fjlmnr':
            result.append(c)
        elif c == 'g':
            if next in 'iey':
                result.append('j')
            elif next not in 'hn':
                result.append('k')
            elif next == 'h' and nextnext and nextnext not in 'aeiou':
                i += 1
        elif c == 'h':
            if i == 0 or next in 'aeiou' or s[i-1] not in 'aeiou':
                result.append('h')
        elif c == 'k':
            if i == 0 or s[i-1] != 'c':
                result.append('k')
        elif c == 'p':
            if next == 'h':
                result.append('f')
                i += 1
            else:
                result.append('p')
        elif c == 'q':
            result.append('k')
        elif c == 's':
            if next == 'h':
                result.append('x')
                i += 1
            elif next == 'i' and nextnext in 'oa':
                result.append('x')
                i += 2
            else:
                result.append('s')
        elif c == 't':
            if next == 'i' and nextnext in 'oa':
                result.append('x')
            elif next == 'h':
                result.append('0')
                i += 1
            elif next != 'c' or nextnext != 'h':
                result.append('t')
        elif c == 'v':
            result.append('f')
        elif c == 'w':
            if i == 0 and next == 'h':
                i += 1
            if nextnext in 'aeiou' or nextnext == '*****':
                result.append('w')
        elif c == 'x':
            if i == 0:
                if next == 'h' or (next == 'i' and nextnext in 'oa'):
                    result.append('x')
                else:
                    result.append('s')
            else:
                result.append('k')
                result.append('s')
        elif c == 'y':
            if next in 'aeiou':
                result.append('y')
        elif c == 'z':
            result.append('s')
        elif c == ' ':
            if len(result) > 0 and result[-1] != ' ':
                result.append(' ')

        i += 1

    return ''.join(result).upper()
