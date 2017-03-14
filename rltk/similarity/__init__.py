from hamming import hamming_distance, hamming_similarity, normalized_hamming_distance
from levenshtein import levenshtein_distance, levenshtein_similarity, \
    normalized_levenshtein_distance, damerau_levenshtein_distance
from needleman import needleman_wunsch_score
from jaro import jaro_winkler_distance, jaro_winkler_similarity, jaro_distance
from jaccard import jaccard_index_similarity, jaccard_index_distance
from cosine import cosine_similarity
from tf_idf import tf_idf_similarity

from soundex import soundex_similarity
from metaphone import metaphone_similarity
from nysiis import nysiis_similarity
