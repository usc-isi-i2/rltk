def q_grams(s, q):
    if q < 1:
        raise ValueError('Wrong parameter')

    PLACEHOLDER = '#'
    s = PLACEHOLDER * (q - 1) + s + PLACEHOLDER * (q - 1)
    return [s[i : i + q] for i in range(len(s) - q + 1)]
