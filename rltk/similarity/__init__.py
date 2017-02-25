from hamming import hamming_distance
from levenshtein import levenshtein_distance, levenshtein_similarity, \
    normalized_levenshtein_distance, damerau_levenshtein_distance
from jaro import jaro_winkler_distance, jaro_winkler_similarity, jaro_distance
from jaccard import jaccard_index_similarity, jaccard_index_distance
from cosine import cosine_distance, cosine_similarity
from tf_idf import tf_idf

from soundex import soundex
from metaphone import metaphone
from nysiis import nysiis


class RLTK(object):

    _init_dict = dict()

    def __init__(self, init_dict):
        _init_dict = init_dict

    def levenshtein_distance(self, s1, s2):
        levenshtein_distance(s1, s2)


def init(**kwargs):
    return RLTK(kwargs)