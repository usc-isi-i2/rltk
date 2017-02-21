import string_similarity


class RLTK():

    _CLASSES = {
        # string similarity
        'levenshtein': string_similarity.levenshtein.Levenshtein,
        'normalized_levenshtein': string_similarity.levenshtein.NormalizedLevenshtein,
        'jaro_winkler': string_similarity.jaro_winkler.JaroWinkler,
        'jaccard_index': string_similarity.jaccard.JaccardIndex,
        'cosine': string_similarity.cosine.Cosine,
        'tf_idf': string_similarity.tf_idf.TfIdf,
    }

    def __init__(self):
        pass

    def __getattr__(self, class_name):

        if class_name in self._CLASSES:
            class_identifier = self._CLASSES[class_name]
            return class_identifier

        raise NameError("%s doesn't exist." % class_name)

def init():
    return RLTK()