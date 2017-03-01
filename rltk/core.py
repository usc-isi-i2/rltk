from similarity import *

class Core(object):

    # resource dict
    # each item should have at least has 2 keys: type, data
    _rs_dict = dict()

    def _has_resource(self, name, type):
        if name not in self._rs_dict or type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name or type')

    def _check_valid_resource(self, name, type):
        if name in self._rs_dict and type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name for resource, it is used by another type')

    def load_edit_distance_table(self, name, cost_dict):
        """
        Load cost table for edit distance.

        Args:
            name (str): Name of the resource.
            cost_dict (dict): The cost of operations.
                insert, delete, substitute (dict): Different costs of characters in each operation.
                insert_default, delete_default, substitute_default (int): Default cost of each operation.

        Examples:
            >>> edit_distance_cost = {'insert': {'c':50}, 'insert_default':100, 'delete_default':100, 'substitute_default':100}
            >>> tk.load_edit_distance_table('A1', edit_distance_cost)
        """
        self._check_valid_resource(name, 'edit_distance_table')

        data = {
            'insert': cost_dict['insert'] if 'insert' in cost_dict else {},
            'delete': cost_dict['delete'] if 'delete' in cost_dict else {},
            'substitute': cost_dict['substitute'] if 'substitute' in cost_dict else {},
            'insert_default': cost_dict['insert_default'] if 'insert_default' in cost_dict else {},
            'delete_default': cost_dict['delete_default'] if 'delete_default' in cost_dict else {},
            'substitute_default': cost_dict['substitute_default'] if 'substitute_default' in cost_dict else {}
        }

        self._rs_dict[name] = {
            'type': 'edit_distance_table',
            'data': data
        }


    def load_df_corpus(self, name, file_path, file_type='text', mode='append', jl_path=None):
        """
        Load document frequency corpus resource.

        Args:
            name (str): Name of the resource.
            file_path (str): Path of the df_corpus file.
            file_type (str): text or json_lines. For text file,
                each line treated as a document and tokens in line should separated by whitespace.
            mode (str): 'append' or 'replace'. Defaults to 'append'.
            jl_path (str): Only works when `file_type` is 'json_lines'.

        Examples:
            >>> tk.load_df_corpus('B1', 'df_corpus_1.txt', file_type='text', mode='append')
        """
        self._check_valid_resource(name, 'df_corpus')

        # get original dict item for appending
        # or create / replace it to a new one
        item = {
            'type': 'df_corpus',
            'data': dict(),
            'doc_size': 0
        } if not (mode == 'update' and name in self._rs_dict) else self._rs_dict[name]

        with open(file_path) as f:
            for line in f:
                token = line.rstrip('\n').split(' ')
                if len(token) == 0: # empty line or error in format
                    continue
                token = set(token)

                # count for token
                for t in token:
                    if t not in item['data']:
                        item['data'][t] = 0
                    item['data'][t] += 1

                # count for docs
                item['doc_size'] += 1

        self._rs_dict[name] = item

    def hamming_distance(self, s1, s2):
        """
        Hamming distance used to measure the minimum number of substitutions required to change one sequence into the
        other.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            int: Hamming distance between two sequences.

        Examples:
            >>> tk.hamming_distance('ab','cd')
            2
            >>> tk.hamming_distance('ab','bc')
            2
            >>> tk.hamming_distance('ab','ab')
            0
        """
        return hamming_distance(s1, s2)

    def levenshtein_similarity(self, s1, s2):
        """
        The Levenshtein similarity is computed as 1 - normalized_levenshtein_distance.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str): Name of resource (edit distance table).

        Returns:
            float: Levenshtein Similarity between [0.0, 1.0].
        """
        return levenshtein_similarity(s1, s2)

    def levenshtein_distance(self, s1, s2, name=None):
        """
        The Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str): Name of resource (edit distance table).

        Returns:
            int: Levenshtein Distance.

        Examples:
            >>> tk.load_edit_distance_table('A1', edit_distance_cost)
            >>> tk.levenshtein_distance('ab', 'abc')
            1
            >>> tk.levenshtein_distance('a', 'abc', name='A1')
            150
        """
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

    def normalized_levenshtein_distance(self, s1, s2):
        """
        This distance is computed as levenshtein distance divided by the length of the longest string. This method
        doesn't support customization of operation cost.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Normalized Levenshtein Distance between [0.0, 1.0].
        """
        return normalized_levenshtein_distance(s1, s2)

    def damerau_levenshtein_distance(self, s1, s2):
        """
        Similar to Levenshtein, Damerau-Levenshtein distance is the minimum number of operations needed to transform one string into the other, where an operation is defined as an insertion, deletion, or substitution of a single character, or a transposition of two adjacent characters.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Damerau Levenshtein Distance.

        Examples:
            >>> tk.damerau_levenshtein_distance('abcd', 'acbd')
            1
            >>> tk.damerau_levenshtein_distance('abbd', 'acad')
            2
        """
        return damerau_levenshtein_distance(s1, s2)

    def jaro_distance(self, s1, s2):
        """
        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Jaro Distance.

        Examples:
            >>> tk.jaro_distance('abc', 'abd')
            0.7777777777777777
            >>> tk.jaro_distance('abccd', 'abcdc')
            0.9333333333333332
        """
        return jaro_distance(self, s1, s2)

    def jaro_winkler_similarity(self, s1, s2, threshold=0.7, scaling_factor=0.1):
        """
        The max length for common prefix is 4.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            threshold (int, optional): Boost threshold, prefix bonus is only added \
                when compared strings have a Jaro Distance above it. Defaults to 0.7.
            scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards \
                for having common prefixes. Defaults to 0.1.

        Returns:
            float: Jaro Winkler Similarity.

        Examples:
            >>> tk.jaro_winkler_similarity('abchello', 'abcworld')
            0.6833333333333332
            >>> tk.jaro_winkler_similarity('hello', 'world')
            0.4666666666666666
        """
        return jaro_winkler_similarity(s1, s2, threshold, scaling_factor)

    def jaro_winkler_distance(self, s1, s2, threshold=0.7, scaling_factor=0.1):
        """
        Jaro Winkler Distance is computed as 1 - jaro_winkler_similarity.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            threshold (int, optional): Boost threshold, prefix bonus is only added when compared strings have\
                a Jaro Distance above it. Defaults to 0.7.
            scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards\
                for having common prefixes. Defaults to 0.1.

        Returns:
            float: Jaro Winkler Similarity.

        Examples:
            >>> tk.jaro_winkler_similarity('abchello', 'abcworld')
            0.6833333333333332
            >>> tk.jaro_winkler_similarity('hello', 'world')
            0.4666666666666666
        """
        return jaro_winkler_distance(s1, s2, threshold, scaling_factor)

    def jaccard_index_similarity(self, set1, set2):
        """
        The Jaccard Index Similarity is then computed as intersection(set1, set2) / union(set1, set2).

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.

        Returns:
            float: Jaccard Index similarity.

        Examples:
            >>> tk.jaccard_index_similarity(set(['a','b']), set(['a','c']))
            0.3333333333333333
            >>> tk.jaccard_index_similarity(set(['a','b']), set(['c','d']))
            0.0
        """
        return jaccard_index_similarity(set1, set2)

    def jaccard_index_distance(self, set1, set2):
        """
        The Jaccard Index Distance is then computed as 1 - jaccard_index_similarity.

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.

        Returns:
            int: Jaccard Index Distance.
        """
        return jaccard_index_distance(set1, set2)

    def cosine_similarity(self, set1, set2):
        """
        The similarity between the two strings is the cosine of the angle between these two vectors representation.

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.

        Returns:
            float: Consine similarity in range [0.0, 1.0].

        Examples:
            >>> tk.cosine_similarity(set([1,2]), set([3,4]))
            0.0
            >>> tk.cosine_similarity(set([1,2]), set([2,3]))
            0.4999999999999999
            >>> tk.cosine_similarity(set([1,2]), set([1,2]))
            0.9999999999999998
        """
        return cosine_similarity(set1, set2)

    def cosine_distance(self, set1, set2):
        """
        Distance of Cosine similarity is computed as 1 - cosine_similarity.

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.

        Returns:
            int: Distance of Consine similarity.
        """
        return cosine_distance(set1, set2)

    def tf_idf(self, bag1, bag2, name, math_log=False):
        """
        Computes TF/IDF measure. This measure employs the notion of TF/IDF score commonly used in information retrieval (IR) to find documents that are relevant to keyword queries. The intuition underlying the TF/IDF measure is that two strings are similar if they share distinguishing terms.

        Args:
            bag1 (list): Bag 1.
            bag2 (list): Bag 2.
            name (str): Name of resource (document frequency corpus).
            math_log (bool, optional): Flag to indicate whether math.log() should be used in TF and IDF formulas. \
                Defaults to False.

        Returns:
            float: TF/IDF similarity.

        Examples:
            >>> tk.tf_idf(['a', 'b', 'a'], ['a', 'c','d','f'], name='B1')
            0.17541160386140586
        """
        self._has_resource(name, 'df_corpus')
        return tf_idf(bag1, bag2, self._rs_dict[name]['data'], self._rs_dict[name]['doc_size'], math_log)

    def soundex(self, s):
        """
        The standard used for this implementation is provided by `U.S. Census Bureau <https://www.archives.gov/research/census/soundex.html>`_.

        Args:
            s (str): Sequence.

        Returns:
            str: Coded sequence.

        Examples:
            >>> tk.soundex('ashcraft')
            'A261'
            >>> tk.soundex('pineapple')
            'P514'
        """
        return soundex(s)

    def metaphone(self, s):
        """
        Metaphone fundamentally improves on the Soundex algorithm by using information about variations and inconsistencies in English spelling and pronunciation to produce a more accurate encoding, which does a better job of matching words and names which sound similar. As with Soundex, similar-sounding words should share the same keys. Metaphone is available as a built-in operator in a number of systems.

        Args:
            s (str): Sequence.

        Returns:
            str: Coded sequence.

        Examples:
            >>> tk.metaphone('ashcraft')
            'AXKRFT'
            >>> tk.metaphone('pineapple')
            'PNPL'
        """
        return metaphone(s)

    def nysiis(self, s):
        """
        New York State Immunization Information System (NYSIIS) Phonetic Code is a phonetic algorithm created by `The New York State Department of Health's (NYSDOH) Bureau of Immunization
        <https://www.health.ny.gov/prevention/immunization/information_system/>`_.

        Args:
            s (str): Sequence.

        Returns:
            str: Coded sequence.

        Examples:
            >>> tk.metaphone('ashcraft')
            'AXKRFT'
            >>> tk.metaphone('pineapple')
            'PNPL'
        """
        return nysiis(s)

