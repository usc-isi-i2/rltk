import math

cpdef double tf_idf_similarity_by_dict(tfidf_dict1, tfidf_dict2):

    cdef double v_x_y = 0.0, v_x_2 = 0.0, v_y_2 = 0.0, tfidf

    # intersection of dict1 and dict2
    # ignore the values that are not in both
    for t in tfidf_dict1.iterkeys():
        if t in tfidf_dict2:
            v_x_y = tfidf_dict1[t] * tfidf_dict2[t]

    for tfidf in tfidf_dict1.itervalues():
        v_x_2 += tfidf * tfidf
    for tfidf in tfidf_dict2.itervalues():
        v_y_2 += tfidf * tfidf

    # cosine similarity
    return v_x_y / (math.sqrt(v_x_2) * math.sqrt(v_y_2))

