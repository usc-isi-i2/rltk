import levenshtein
import jaro_winkler
import jaccard

class RLTK():

    _CLASSES = {
        'levenshtein': levenshtein.Levenshtein,
        'normalized_levenshtein': levenshtein.NormalizedLevenshtein,
        'jaro_winkler': jaro_winkler.JaroWinkler,
        'jaccard_index': jaccard.JaccardIndex,
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