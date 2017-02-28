from similarity import *

class RLTK(object):

    # resource dict
    # each item should have at least has 2 keys: type, data
    _rs_dict = dict()

    def _has_resource(self, name, type):
        if name not in self._rs_dict or type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name or type')

    def _check_valid_resource(self, name, type):
        if name in self._rs_dict and type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name for resource, it is used by another type')

    def load_edit_distance_table(self, name, insert={}, delete={}, substitute={},
                           insert_default=1, delete_default=1, substitute_default=1):

        self._check_valid_resource(name, 'edit_distance_table')

        data = {
            'insert': insert,
            'delete': delete,
            'substitute': substitute,
            'insert_default': insert_default,
            'delete_default': delete_default,
            'substitute_default': substitute_default
        }

        self._rs_dict[name] = {
            'type': 'edit_distance_table',
            'data': data
        }


    def load_df_corpus(self, name, file_path, file_type='text', mode='update', jl_path=None):
        self._check_valid_resource(name, 'df_corpus')

        # get original dict item for update
        # or create / replace it to a new one
        item = {
            'type': 'df_corpus',
            'data': dict(),
            'total_documents': 0
        } if not (mode == 'update' and name in self._rs_dict) else self._rs_dict[name]

        with open(file_path) as f:
            for line in f:
                token = line.rstrip('\n')

                # count
                if token not in item['data']:
                    item['data'][token] = 0
                item['data'][token] += 1

        item['total_documents'] += 1
        self._rs_dict[name] = item

    def hamming_distance(self, s1, s2):
        return hamming_distance(s1, s2)

    def levenshtein_similarity(self, s1, s2, name=None):
        if name is None:
            return levenshtein_similarity(s1, s2)
        else:
            self._has_resource(name, 'edit_distance_table')

            insert = self._rs_dict[name]['data']['insert']
            delete = self._rs_dict[name]['data']['delete']
            substitute = self._rs_dict[name]['data']['substitute']
            insert_default = self._rs_dict[name]['data']['insert_default']
            delete_default = self._rs_dict[name]['data']['delete_default']
            substitute_default = self._rs_dict[name]['data']['substitute_default']
            return levenshtein_similarity(s1, s2, insert, delete, substitute,
                               insert_default, delete_default, substitute_default)

    def levenshtein_distance(self, s1, s2, name=None):
        if name is None:
            return levenshtein_distance(s1, s2)
        else:
            self._has_resource(name, 'edit_distance_table')

            insert = self._rs_dict[name]['data']['insert']
            delete = self._rs_dict[name]['data']['delete']
            substitute = self._rs_dict[name]['data']['substitute']
            insert_default = self._rs_dict[name]['data']['insert_default']
            delete_default = self._rs_dict[name]['data']['delete_default']
            substitute_default = self._rs_dict[name]['data']['substitute_default']
            return levenshtein_distance(s1, s2, insert, delete, substitute,
                               insert_default, delete_default, substitute_default)

    def normalized_levenshtein_distance(self, s1, s2, name=None):
        if name is None:
            return normalized_levenshtein_distance(s1, s2)
        else:
            self._has_resource(name, 'edit_distance_table')

            insert = self._rs_dict[name]['data']['insert']
            delete = self._rs_dict[name]['data']['delete']
            substitute = self._rs_dict[name]['data']['substitute']
            insert_default = self._rs_dict[name]['data']['insert_default']
            delete_default = self._rs_dict[name]['data']['delete_default']
            substitute_default = self._rs_dict[name]['data']['substitute_default']
            return normalized_levenshtein_distance(s1, s2, insert, delete, substitute,
                               insert_default, delete_default, substitute_default)

    def damerau_levenshtein_distance(self, s1, s2):
        return damerau_levenshtein_distance(s1, s2)

    def jaro_distance(self, s1, s2):
        return jaro_distance(self, s1, s2)

    def jaro_winkler_similarity(self, s1, s2, threshold=0.7, scaling_factor=0.1):
        return jaro_winkler_similarity(s1, s2, threshold, scaling_factor)

    def jaro_winkler_distance(self, s1, s2, threshold=0.7, scaling_factor=0.1):
        return jaro_winkler_distance(s1, s2, threshold, scaling_factor)

    def jaccard_index_similarity(self, set1, set2):
        return jaccard_index_similarity(set1, set2)

    def jaccard_index_distance(self, set1, set2):
        return jaccard_index_distance(set1, set2)

    def cosine_similarity(self, set1, set2):
        return cosine_similarity(set1, set2)

    def cosine_distance(self, set1, set2):
        return cosine_distance(set1, set2)

    # def tf_idf(self, bag1, bag2, name, dampen=False):
    #     self._check_valid_resource(name, 'df_corpus')
    #
    #     corpus_list = self._get_value('tf_idf.corpus_list')
    #     return tf_idf(bag1, bag2, corpus_list, dampen)

    def soundex(self, s):
        return soundex(s)

    def metaphone(self, s):
        return metaphone(s)

    def nysiis(self, s):
        return nysiis(s)

