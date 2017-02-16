class Levenshtein(object):

    _similarity = 0
    _distance = 0

    def __init__(self, s1, s2):
        def helper(str1, n1, str2, n2):
            """
            code from niR@github https://github.com/pupuhime
            time: O(n1*n2)
            space: O(n1*n2)
            """
            lev_matrix = [[0 for i1 in range(n1 + 1)] for i2 in range(n2 + 1)]
            for i1 in range(1, n1 + 1):
                lev_matrix[0][i1] = i1
            for i2 in range(1, n2 + 1):
                lev_matrix[i2][0] = i2
            for i2 in range(1, n2 + 1):
                for i1 in range(1, n1 + 1):
                    cost = 0 if str1[i1 - 1] == str2[i2 - 1] else 1
                    elem = min(lev_matrix[i2 - 1][i1] + 1,
                               lev_matrix[i2][i1 - 1] + 1,
                               lev_matrix[i2 - 1][i1 - 1] + cost)
                    lev_matrix[i2][i1] = elem
            return lev_matrix[-1][-1]

        if s1 is None or s2 is None:
            raise ValueError()
            return

        n1, n2 = len(s1), len(s2)
        if n1 == 0 and n2 == 0:
            self._distance = 0
            self._similarity = 1
            return

        if n1 == 0 or n2 == 0:
            self._distance = max(n1, n2)
        else:
            self._distance = helper(s1, n1, s2, n2)
        self._similarity = 1 - float(self._distance) / max(n1, n2)

    def similarity(self):
        return self._similarity

    def distance(self):
        return self._distance

class NormalizedLevenshtein(object):

    _similarity = 0
    _distance = 0

    def __init__(self, s1, s2):
        lev = Levenshtein(s1, s2)

        n1, n2 = len(s1), len(s2)
        max_len = max(n1, n2)
        if max_len == 0:
            return # same as the Levenshtein

        self._distance = float(lev.distance()) / max_len
        self._similarity = 1 - self._distance


    def similarity(self):
        return self._similarity

    def distance(self):
        return self._distance
