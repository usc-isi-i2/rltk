from hamming import hamming_distance
from levenshtein import levenshtein_distance, levenshtein_similarity, normalized_levenshtein_distance, \
    normalized_levenshtein_similarity, damerau_levenshtein_distance
from jaro import jaro_winkler_distance, jaro_winkler_similarity, jaro_distance
from jaccard import jaccard_index_similarity, jaccard_index_distance
from cosine import cosine_distance, cosine_similarity
from tf_idf import tf_idf_similarity

from soundex import soundex
from metaphone import metaphone
from nysiis import nysiis