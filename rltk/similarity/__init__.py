# common distance
from rltk.similarity.distance import euclidean_distance, euclidean_similarity, \
    manhattan_distance, manhattan_similarity

# normal
from rltk.similarity.equal import string_equal, number_equal
from rltk.similarity.hamming import hamming_distance, hamming_similarity, normalized_hamming_distance
from rltk.similarity.dice import dice_similarity
from rltk.similarity.levenshtein import levenshtein_distance, levenshtein_similarity, \
    damerau_levenshtein_distance, damerau_levenshtein_similarity, \
    optimal_string_alignment_distance, optimal_string_alignment_similarity
from rltk.similarity.needleman import needleman_wunsch_score, needleman_wunsch_similarity
from rltk.similarity.jaro import jaro_winkler_distance, jaro_winkler_similarity, jaro_distance
from rltk.similarity.jaccard import jaccard_index_similarity, jaccard_index_distance
from rltk.similarity.cosine import cosine_similarity, string_cosine_similarity
from rltk.similarity.tf_idf import tf_idf_similarity, compute_idf, compute_tf, tf_idf_cosine_similarity, TF_IDF
from rltk.similarity.lcs import longest_common_subsequence_distance, metric_longest_common_subsequence
from rltk.similarity.ngram import ngram_distance, ngram_similarity
from rltk.similarity.qgram import qgram_distance, qgram_similarity

# # hybrid
from rltk.similarity.hybrid import hybrid_jaccard_similarity, monge_elkan_similarity, symmetric_monge_elkan_similarity

# # phonetic
from rltk.similarity.soundex import soundex_similarity, soundex
from rltk.similarity.metaphone import metaphone_similarity, metaphone
from rltk.similarity.nysiis import nysiis_similarity, nysiis
