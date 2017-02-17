from tokenizer import q_grams
import utils

class JaccardIndex(object):

    _similarity = 0

    def __init__(self, s1, s2, token_size = 2):
        utils.check_for_none(s1, s2)
        utils.check_for_type(str, s1, s2)

        set1, set2 = set(q_grams(s1, token_size)), set(q_grams(s2, token_size))
        self._similarity = float(len(set1 & set2)) / float(len(set1 | set2))

    def similarity(self):
        return self._similarity

    def distance(self):
        return 1 - self._similarity

