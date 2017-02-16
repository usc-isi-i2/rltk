from .levenshtein import Levenshtein

class RLTK():

    _CLASSES = {
        'levenshtein': levenshtein.Levenshtein,
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