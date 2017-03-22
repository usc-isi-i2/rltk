import collections
import math

import utils


def tf_idf_similarity(bag1, bag2, df_corpus, doc_size, math_log=False):
    """
    Computes TF/IDF measure. This measure employs the notion of TF/IDF score commonly used in information retrieval (IR) to find documents that are relevant to keyword queries. The intuition underlying the TF/IDF measure is that two strings are similar if they share distinguishing terms.

    Args:
        bag1 (list): Bag 1.
        bag2 (list): Bag 2.
        df_corpus (dict): The pre calculated document frequency of corpus.
        doc_size (int): total documents used in corpus.
        math_log (bool, optional): Flag to indicate whether math.log() should be used in TF and IDF formulas. Defaults to False.

    Returns:
        float: TF/IDF cosine similarity.

    Examples:
        >>> rltk.tfidf(['a', 'b', 'a'], ['a', 'c'], {'a':3, 'b':1, 'c':1}, 3)
        0.17541160386140586
        >>> rltk.tfidf(['a', 'b', 'a'], ['a', 'c'], {'a':3, 'b':2, 'c':1}, 4, True)
        0.12977804138
        >>> rltk.tfidf(['a', 'b', 'a'], ['a'], {'a':3, 'b':1, 'c':1}, 3)
        0.5547001962252291
    """
    # http://www.tfidf.com/

    utils.check_for_none(bag1, bag2, df_corpus)
    utils.check_for_type(list, bag1, bag2)

     # term frequency for input strings
    t_x, t_y = collections.Counter(bag1), collections.Counter(bag2)
    tf_x = {k: float(v) / len(bag1) for k, v in t_x.iteritems()}
    tf_y = {k: float(v) / len(bag2) for k, v in t_y.iteritems()}

    # unique element
    total_unique_elements = set()
    total_unique_elements.update(bag1)
    total_unique_elements.update(bag2)

    idf_element, v_x, v_y, v_x_y, v_x_2, v_y_2 = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    # tfidf calculation
    for element in total_unique_elements:
        if element not in df_corpus:
            continue
        idf_element = doc_size * 1.0 / df_corpus[element]

        v_x = 0 if element not in tf_x else (math.log(idf_element) * tf_x[element]) if math_log else (
            idf_element * tf_x[element])
        v_y = 0 if element not in tf_y else (math.log(idf_element) * tf_y[element]) if math_log else (
            idf_element * tf_y[element])
        v_x_y += v_x * v_y
        v_x_2 += v_x * v_x
        v_y_2 += v_y * v_y

    # cosine similarity
    return 0.0 if v_x_y == 0 else v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))
