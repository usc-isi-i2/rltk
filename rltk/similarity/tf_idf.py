import collections
import math

import utils


def _tf_idf(bag1, bag2, df_corpus, doc_size, math_log):

    utils.check_for_none(bag1, bag2, df_corpus)
    utils.check_for_type(list, bag1, bag2)

     # term frequency for input strings
    tf_x, tf_y = collections.Counter(bag1), collections.Counter(bag2)

    # unique element
    total_unique_elements = set()
    total_unique_elements.update(bag1)
    total_unique_elements.update(bag2)

    idf_element, v_x, v_y, v_x_y, v_x_2, v_y_2 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    # tfidf calculation
    for element in total_unique_elements:
        if element not in df_corpus:
            continue
        idf_element = doc_size * 1.0 / (df_corpus[element] if element in df_corpus else 1)
        v_x = 0 if element not in tf_x else (math.log(idf_element) * math.log(tf_x[element] + 1)) if math_log else (
            idf_element * tf_x[element])
        v_y = 0 if element not in tf_y else (math.log(idf_element) * math.log(tf_y[element] + 1)) if math_log else (
            idf_element * tf_y[element])
        v_x_y += v_x * v_y
        v_x_2 += v_x * v_x
        v_y_2 += v_y * v_y

    # cosine similarity
    return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))

def tf_idf(bag1, bag2, df_corpus, doc_size, math_log=False):
    """
    Computes TF/IDF measure. This measure employs the notion of TF/IDF score commonly used in information retrieval (IR) to find documents that are relevant to keyword queries. The intuition underlying the TF/IDF measure is that two strings are similar if they share distinguishing terms.

    Args:
        bag1 (list): Bag 1.
        bag2 (list): Bag 2.
        corpus_list (list(list), optional): The corpus that will be used to compute TF and IDF values. This corpus is a list of strings, where each string has been tokenized into a list of tokens (that is, a bag of tokens). Defaults is to None.
        dampen (bool, optional): Flag to indicate whether math.log() should be used in TF and IDF formulas. Defaults to False.

    Returns:
        float: TF/IDF score.

    Examples:
        >>> rltk.tfidf(['a', 'b', 'a'], ['a', 'c'], [['a', 'b', 'a'], ['a', 'c'], ['a']])
        0.17541160386140586
        >>> rltk.tfidf(['a', 'b', 'a'], ['a', 'c'], [['a', 'b', 'a'], ['a', 'c'], ['a'], ['b']], True)
        0.11166746710505392
        >>> rltk.tfidf(['a', 'b', 'a'], ['a'], [['a', 'b', 'a'], ['a', 'c'], ['a']])
        0.5547001962252291
    """
    return _tf_idf(bag1, bag2, df_corpus, doc_size, math_log)


# def tf_idf_original(bag1, bag2, corpus_list=None, dampen=False):
#     return _tf_idf_original(bag1, bag2, corpus_list, dampen)
#
# def _tf_idf_original(bag1, bag2, corpus_list, dampen):
#     # code modified from py_stringmatching
#     # Copyright (c) 2016, anhaidgroup
#     # All rights reserved.
#
#     utils.check_for_none(bag1, bag2)
#     utils.check_for_type(list, bag1, bag2)
#
#     # if corpus is not provided treat input string as corpus
#     if corpus_list is None:
#         corpus_list = [bag1, bag2]
#     corpus_size = len(corpus_list)
#
#      # term frequency for input strings
#     tf_x, tf_y = collections.Counter(bag1), collections.Counter(bag2)
#
#     # number of documents an element appeared
#     element_freq = {}
#
#     # set of unique element
#     total_unique_elements = set()
#     for document in corpus_list:
#         temp_set = set()
#         for element in document:
#             # adding element only if it is present in one of two input string
#             if element in bag1 or element in bag2:
#                 temp_set.add(element)
#                 total_unique_elements.add(element)
#
#         # update element document frequency for this document
#         for element in temp_set:
#             element_freq[element] = element_freq[element] + 1 if element in element_freq else 1
#     idf_element, v_x, v_y, v_x_y, v_x_2, v_y_2 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
#
#     # tfidf calculation
#     for element in total_unique_elements:
#         idf_element = corpus_size * 1.0 / element_freq[element]
#         v_x = 0 if element not in tf_x else (math.log(idf_element) * math.log(tf_x[element] + 1)) if dampen else (
#             idf_element * tf_x[element])
#         v_y = 0 if element not in tf_y else (math.log(idf_element) * math.log(tf_y[element] + 1)) if dampen else (
#             idf_element * tf_y[element])
#         v_x_y += v_x * v_y
#         v_x_2 += v_x * v_x
#         v_y_2 += v_y * v_y
#
#     return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))