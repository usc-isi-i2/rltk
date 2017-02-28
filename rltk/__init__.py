from core import *

def init():
    return RLTK()

# def init(init_dict):
#     """
#     This is the method for loading all configurations into memory. Once initialized, invoke methods without passing
#     those gigantic structure again and again.
#
#     Args:
#         init_dict (dict):
#             'levenshtein.insert'
#             'levenshtein.delete'
#             'levenshtein.substitute'
#             'levenshtein.insert_default'
#             'levenshtein.delete_default'
#             'levenshtein.substitute_default'
#             'tf_idf.corpus_list'
#
#     Returns:
#         object: wrapped object
#
#     Examples:
#         >>> import rltk
#         >>> tk = rltk.init({'tf_idf.corpus_list': [['a', 'b', 'a'], ['a', 'c'], ['a']]})
#         >>> tk.levenshtein_distance('a', 'ab')
#         0.5
#         >>> tk.tf_idf(['a', 'b', 'a'], ['a', 'c'])
#         0.17541160386140586
#     """
#     return RLTK(init_dict)