import __builtin__
import json
import os
import logging
import collections
import pickle

from jsonpath_rw import parse
from tokenizer.digCrfTokenizer.crf_tokenizer import CrfTokenizer

import utils
from configuration import Configuration
from file_iterator import FileIterator
from similarity import *
if __builtin__.rltk['enable_cython']:
    # override non-cython version
    from similarity.cython import *
from classifier import *
from indexer import *


class Core(object):

    # resource dict
    # each item should have at least has 2 keys: type, data
    _rs_dict = dict()

    # absolute root path for all relative paths in configurations
    _root_path = ''

    # logger and logger settings
    _logger = None
    _logger_config = {
        'file_path': 'log.log',
        'level': 'info',
        'format': '%(asctime)s %(levelname)s %(message)s'
    }

    def __init__(self):
        self.set_root_path('.')
        self.update_logging_settings()
        self._crf_tokenizer = CrfTokenizer()

    def _has_resource(self, name, type):
        if name not in self._rs_dict or type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name or type')

    def _check_valid_resource(self, name, type):
        if name in self._rs_dict and type != self._rs_dict[name]['type']:
            raise ValueError('Invalid name for resource, it is used by another type')

    def update_logging_settings(self, file_path=None, level=None, format=None):
        """
        Update global logging. If None is set to the arguments, it will keep the previous setting.

        Args:
            file_path (str): It is Initialized to 'log.log'.
            level (str): It can be 'error', 'warning' or 'info'. It is Initialized to 'error'.
            format (str): It is Initialized to '%(asctime)s %(levelname)s %(message)s'.
        """

        LOGGING_STRING_MAP = {'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR}
        if file_path is not None:
            self._logger_config['file_path'] = self._get_abs_path(file_path)
        if level is not None:
            self._logger_config['level'] = level
        if format is not None:
            self._logger_config['format'] = format

        logger = logging.getLogger(Configuration.LOGGER_NAME)
        log_file = logging.FileHandler(self._logger_config['file_path'])
        logger.addHandler(log_file)
        log_file.setFormatter(logging.Formatter(self._logger_config['format']))
        logger.setLevel(LOGGING_STRING_MAP[self._logger_config['level']])
        self._logger = logger

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

    def load_alignment_score_matrix(self, name, score_dict):
        """
        Load alignment score matrix for alignment measure methods like Needleman-Wunsch.

        Args:
            name (str): Name of the resource.
            score_dict (dict): Alignment score matrix.

        Examples:
            >>> score_table = {'a': {'c': 3}, 'e': {'f': 9, 'k': 1}}
            >>> tk.load_edit_distance_table('D1', score_table)
        """
        self._check_valid_resource(name, 'alignment_score_matrix')

        self._rs_dict[name] = {
            'type': 'alignment_score_matrix',
            'data': score_dict
        }


    def load_df_corpus(self, name, file_path, file_type='text', mode='append', json_path=None):
        """
        Load document frequency corpus resource.

        Args:
            name (str): Name of the resource.
            file_path (str): Path of the df_corpus file.
            file_type (str, optional): 'text' or 'json_lines'.
                For text file, each line is treated as a document and tokens in line should separated by whitespace.
                For json line file, each json object is treated as a document. `json_path` should be \
                set and point to an array of strings which will be \
                tokenized by `dig-crf-tokenizer <https://github.com/usc-isi-i2/dig-crf-tokenizer>`_.
            mode (str, optional): 'append' or 'replace'. Defaults to 'append'.
            json_path (str, optional): Only works when `file_type` is 'json_lines'.

        Examples:
            >>> tk.load_df_corpus('B1', 'df_corpus_1.txt', file_type='text', mode='replace')
            >>> tk.load_df_corpus('B2', 'jl_file_1.jsonl', file_type='json_lines', json_path='desc[*]')
        """
        def count_for_token(tokens_):
            for t in tokens_:
                item['data'][t] = item['data'].get(t, 0) + 1
                # if t not in item['data']:
                #     item['data'][t] = 0
                # item['data'][t] += 1

        self._check_valid_resource(name, 'df_corpus')

        if file_type not in ('text', 'json_lines'):
            raise ValueError('Unsupported file type')

        # get original dict item for appending
        # or create / replace it to a new one
        item = {
            'type': 'df_corpus',
            'data': dict(),
            'docs_size': 0
        } if not (mode == 'append' and name in self._rs_dict) else self._rs_dict[name]

        if file_type == 'text':
            with open(self._get_abs_path(file_path), 'r') as f:
                for line in f:
                    line = line.rstrip('\n')

                    tokens = line.split(' ')
                    if len(tokens) == 0:
                        continue
                    tokens = set(tokens)
                    count_for_token(tokens)

                # count for docs (each line is a doc)
                item['docs_size'] += 1

        elif file_type == 'json_lines':
            if json_path is None:
                raise ValueError('Invalid json path')
            with open(self._get_abs_path(file_path), 'r') as f:
                parse_jl = parse(json_path)
                for line in f:
                    line = line.rstrip('\n')

                    line = json.loads(line)
                    matches = parse_jl.find(line)
                    doc_parts = [match.value for match in matches]
                    if len(doc_parts) == 0:
                        continue

                    for part in doc_parts:
                        if not isinstance(part, basestring):
                            raise TypeError('json_path must points to an array of strings')
                        tokens = self._crf_tokenizer.tokenize(part)
                        count_for_token(tokens)

                    # count for docs (each line is a doc)
                    item['docs_size'] += 1

        self._rs_dict[name] = item

    def _increase_df_corpus(self, df_corpus, terms):
        """
        check if name is valid before using by
        self._check_valid_resource(name, 'df_corpus')
        and also check it is actually exist by calling _get_df_corpus
        """
        for t in terms:
            df_corpus['data'][t] = df_corpus['data'].get(t, 0) + 1

    def _get_df_corpus(self, name):
        self._check_valid_resource(name, 'df_corpus')

        if name not in self._rs_dict:
            item = {
                'type': 'df_corpus',
                'data': dict(),
                'docs': dict(), #
                'docs_size': 0,
                'idf': dict(),
                # once new doc added, fresh should be false,
                # idf and all the tfidf in docs should be re-computed
                'fresh': True
            }
            self._rs_dict[name] = item

        return self._rs_dict[name]

    def load_document_data(self, corpus_name, doc_name, tokens):

        self._check_valid_resource(corpus_name, 'df_corpus')
        df_corpus = self._get_df_corpus(corpus_name)

        doc_item = {
            'tf': dict(), # term frequency
            'tf_idf': dict(), # precomputed tfidf score
        }

        if len(tokens) != 0:
            counted_terms = collections.Counter(tokens)
            doc_item['tf'] = compute_tf(counted_terms, len(tokens))
            df_corpus['docs'][doc_name] = doc_item
            df_corpus['docs_size'] += 1
            self._increase_df_corpus(df_corpus, counted_terms.keys())
            df_corpus['fresh'] = False

    def load_documents(self, corpus_name, file_path, auto_name=False, name_json_path=None, doc_json_path=None):
        parse_name = parse(name_json_path) if name_json_path is not None else None
        parse_doc = parse(doc_json_path)
        i = 0
        with open(self._get_abs_path(file_path), 'r') as f:
            for line in f:
                line = json.loads(line.rstrip('\n'))
                matches_name = [match.value for match in parse_name.find(line)] \
                    if name_json_path is not None else None
                matches_doc = [match.value for match in parse_doc.find(line)]
                if len(matches_doc) == 0:
                    continue
                if auto_name:
                    self.load_document_data(corpus_name, i, matches_doc[0])
                    i += 1
                else:
                    self.load_document_data(corpus_name, matches_name[0], matches_doc[0])

    def load_feature_configuration(self, name, file_path):
        """
        Load feature configuration resource.

        Args:
            name (str): Name of the resource.
            file_path (str): Path of the feature configuration file. This file should be formatted in json.

        Examples:
            >>> tk.load_feature_configuration('C1', 'feature_config_1.json')

            Content of configuration file (please remove all comments before using):

            .. code-block:: javascript

                {
                    // default value for missing result value.
                    "missing_value_default": 0,
                    // ignore or exception.
                    "error_handling": "exception",
                    // feature vectors
                    "features": [
                        {
                            // function.
                            "function": "levenshtein_distance",
                            // json path for fields.
                            // only need one element if json dicts have the same structure.
                            "json_path": ["gender", "$.person.gender"],
                            // optional, format the extracted entities
                            "after_extraction": ["lambda x: set(x.split(' '))"],
                            // optional, other parameters that need to be used in function.
                            "other_parameters": {},
                            // optional, the content of file should be a json dict.
                            // If `other_parameters` is set, this value will be ignored.
                            "other_parameters_file_path": "lev_parameters_1.json"
                        },
                        ...
                    ]
                }


        """
        self._check_valid_resource(name, 'feature_configuration')

        item = {
            'name': name,
            'type': 'feature_configuration',
            'data': None
        }
        with open(self._get_abs_path(file_path), 'r') as f:
            config = json.loads(f.read())

            # missing value default
            if 'missing_value_default' not in config:
                raise ValueError('Missing value of missing_value_default')

            # error handling
            if 'error_handling' not in config:
                raise ValueError('Missing value of error_handling')
            else:
                if config['error_handling'] not in ('ignore', 'exception'):
                    raise ValueError('Invalid value of error_handling')

            # features (pre-compiled)
            if 'features' not in config:
                raise ValueError('Missing value of features')
            for idx, feature in enumerate(config['features']):

                # function pointer
                feature['function'] = getattr(self, feature['function'])

                # json path
                if 'json_path' not in feature or len(feature['json_path']) == 0:
                    raise ValueError('Missing value of json_path')
                if len(feature['json_path']) >= 1:
                    feature['json_path'][0] = parse(feature['json_path'][0])
                if len(feature['json_path']) == 2:
                    feature['json_path'][1] = parse(feature['json_path'][1])

                # get first
                if 'get_first' not in feature:
                    feature['get_first'] = True

                # tokenizer
                if 'use_tokenizer' not in feature:
                    feature['use_tokenizer'] = False

                # other parameters
                if 'other_parameters' not in feature:
                    feature['other_parameters'] = {}
                    if 'other_parameters_file_path' in feature:
                        with open(self._get_abs_path(feature['other_parameters_file_path'])) as f:
                            feature['other_parameters'] = json.loads(f.read())
                if 'function' in feature['other_parameters']:
                    # for hybrid measures, convert inner function string to reference
                    feature['other_parameters']['function'] = getattr(self, feature['other_parameters']['function'])


            item['data'] = config
            self._rs_dict[name] = item

    def _compute_feature_vector(self, obj1, obj2, name):
        """
        Compute feature vector for two objects.

        Args:
            obj1 (dict): Object1, json dict.
            obj2 (dict): Object2, json dict.
            name (str): Name of resource (feature configuration).

        Returns:
            dict: feature vector.

        Examples:
            >>> tk.load_feature_configuration('C1', 'feature_config_1.json')
            >>> print tk.compute_feature_vector(j1, j2, name='C1')
            {'id': [1, '2'], 'feature_vector': [0.33333333333333337, 1.0]}
        """
        self._has_resource(name, 'feature_configuration')

        config = self._rs_dict[name]['data']
        logger = self._logger
        vector = []

        # process
        for idx, feature in enumerate(config['features']):
            try:
                # function pointer
                feature_function = feature['function']

                # json path
                matches1 = feature['json_path'][0].find(obj1)
                p1 = [match.value for match in matches1]
                matches2 = None
                if len(feature['json_path']) > 1:
                    matches2 = feature['json_path'][1].find(obj2)
                else:
                    matches2 = feature['json_path'][0].find(obj2)
                p2 = [match.value for match in matches2]

                # get first
                if feature['get_first'] is True:
                    if len(p1) == 0:
                        raise ValueError('Missing value in Object1 by json_path \'{0}\''
                                         .format(feature['json_path'][0]))
                    if len(p2) == 0:
                        raise ValueError('Missing value in Object2 by json_path \'{0}\''
                                         .format(feature['json_path'][1]))
                    p1, p2 = p1[0], p2[0]

                # tokenizer
                if feature['use_tokenizer'] is True:
                    p1 = self._crf_tokenizer.tokenize(p1)
                    p2 = self._crf_tokenizer.tokenize(p2)
                    # p1 = filter(None, p1)
                    # p2 = filter(None, p2)

                # other parameters
                other_parameters = feature['other_parameters']

                # run
                ret = feature_function(p1, p2, **other_parameters)

                vector.append(ret)
            except Exception as e:
                logger.error('[{0}-{1}] {2}'.format(name, idx, e.message))
                if config['error_handling'] == 'exception':
                    raise e
                else: # ignore
                    pass
                vector.append(config['missing_value_default'])

        # return vector
        return vector

    def compute_labeled_features(self, iter1, label_path, feature_config_name, feature_output_path, iter2=None):
        """
        Args:
            iter1 (FileIterator): File iterator 1.
            iter2 (FileIterator, optional): File iterator 2. \
                Set it to None if it is a de-duplication task. Defaults to None.
            label_path (str): Path of the label file.
            feature_config_name (str): Name of resource (feature configuration).
            feature_output_path (str): Output path of labelled features.
        """
        self._has_resource(feature_config_name, 'feature_configuration')

        labels = {}
        with open(self._get_abs_path(label_path), 'r') as f:
            for line in f:
                j = json.loads(line)
                id1, id2 = j['id'][0], j['id'][1]
                labels[id1] = labels.get(id1, {})
                labels[id1][id2] = labels.get(id2, j['label'])

        with open(self._get_abs_path(feature_output_path), 'w') as output:
            for id1, value1 in iter1:
                if id1 not in labels:
                    continue
                curr_iter2 = next(iter1.copy()) if iter2 is None else iter2.copy()
                for id2, value2 in curr_iter2:
                    if id2 not in labels[id1]:
                        continue
                    v = self._compute_feature_vector(value1, value2, feature_config_name)

                    ret_dict = {
                        'id': [id1, id2],
                        'feature_vector': v,
                        'label': labels[id1][id2]
                    }
                    output.write(json.dumps(ret_dict))
                    output.write('\n')

    def compute_features(self, iter1, feature_config_name, feature_output_path, iter2=None, blocking_path=None):
        """
        Args:
            iter1 (FileIterator): File iterator 1.
            iter2 (FileIterator, optional): File iterator 2. \
                Set it to None if it is a de-duplication task. Defaults to None.
            feature_config_name (str): Name of resource (feature configuration).
            feature_output_path (str): Output path of labelled features.
            blocking_path (str, optional): If it is not provided, features of all possible pairs will be computed. \
                Defaults to None.
        """
        self._has_resource(feature_config_name, 'feature_configuration')

        blocking = {}
        if blocking_path is not None:
            with open(self._get_abs_path(blocking_path), 'r') as f:
                for line in f:
                    j = json.loads(line)
                    for k, v in j.iteritems():
                        blocking[k] = set(v)

        # if there's no blocking, compare all the possible pairs, O(n^2)
        with open(self._get_abs_path(feature_output_path), 'w') as output:
            for id1, value1 in iter1:
                if blocking_path is not None and id1 not in blocking:
                    continue
                # if iter2 exists, it always iterate from start;
                # else starts from the next element of iter1
                curr_iter2 = next(iter1.copy()) if iter2 is None else iter2.copy()
                for id2, value2 in curr_iter2:
                    if blocking_path is not None and id2 not in blocking[id1]:
                        continue
                    v = self._compute_feature_vector(value1, value2, feature_config_name)
                    ret_dict = {
                        'id': [id1, id2],
                        'feature_vector': v
                    }
                    output.write(json.dumps(ret_dict))
                    output.write('\n')

    # def featurize_ground_truth(self, feature_file_path, ground_truth_file_path, output_file_path=None):
    #     """
    #     Featurize the ground truth by feature vector.
    #
    #     Args:
    #         feature_file_path (str): Json line file of feature vector dicts. \
    #             Each json object should contains a field of id with the array of two elements.
    #         ground_truth_file_path (str): Json line file of ground truth.\
    #             Each json object should contains a field of id with the array of two elements. \
    #             It also need to contains a field named `label` for ground truth.
    #         output_file_path (str, optional): If it is None, the featurized ground truth will print to STDOUT. \
    #             Defaults to None.
    #     """
    #     def hashed_id(ids):
    #         if len(ids) != 2:
    #             raise ValueError('Incorrect number of id')
    #         ids = sorted(ids)
    #
    #         # in order to solve the collision in hashing differentiate types of data
    #         # and to keep just one level comparison of hash key,
    #         # add fixed length of type mark first
    #         # here str != unicode (maybe it needs to compare on their base class basestring)
    #         return '{0}-{1}-{2}-{3}'\
    #             .format(type(ids[0]).__name__, type(ids[1]).__name__, str(ids[0]), str(ids[1]))
    #
    #     # read ground truth into memory
    #     ground_truth = dict()
    #     with open(self._get_abs_path(ground_truth_file_path), 'r') as f:
    #         for line in f:
    #             data = json.loads(line)
    #             k, v = hashed_id(data['id']), data['label']
    #             ground_truth[k] = v
    #
    #     # featurize feature file
    #     if output_file_path is None:
    #         with open(self._get_abs_path(feature_file_path), 'r') as f:
    #             for line in f:
    #                 data = json.loads(line)
    #                 k = hashed_id(data['id'])
    #                 if k in ground_truth:
    #                     data['label'] = ground_truth[k]
    #                     print data
    #     else:
    #         with open(self._get_abs_path(feature_file_path), 'r') as f:
    #             with open(self._get_abs_path(output_file_path), 'w') as out:
    #                 for line in f:
    #                     data = json.loads(line)
    #                     k = hashed_id(data['id'])
    #                     if k in ground_truth:
    #                         data['label'] = ground_truth[k]
    #                         out.write(json.dumps(data))
    #                         out.write('\n')

    # def train_classifier(self, featurized_ground_truth, config):
    #     """
    #     Using featurized ground truth to train classifier.
    #
    #     Args:
    #         featurized_ground_truth (dict): Array of featurized ground truth json dicts.
    #         config (dict): Configuration dict of classifier and parameters includes `function`, \
    #             `function_parameters` and `model_parameter`. \
    #             It accepts `svm`, `k_neighbors`, `gaussian_process`, `decision_tree`, \
    #             `random_forest`, `ada_boost`, `mlp`, `gaussian_naive_bayes`, `quadratic_discriminant_analysis` \
    #             as function.
    #
    #     Returns:
    #         Object: Model of the classifier.
    #     """
    #     x, y = [], []
    #     for obj in featurized_ground_truth:
    #         x.append(obj['feature_vector'])
    #         y.append(obj['label'])
    #
    #     # train
    #     function = get_classifier_class(config['function'])
    #     if 'function_parameters' not in config:
    #         config['function_parameters'] = {}
    #     if 'model_parameters' not in config:
    #         config['model_parameters'] = {}
    #     return function(**config['function_parameters']).fit(x, y, **config['model_parameters'])

    def train_model(self, training_path, classifier, classifier_config={}, model_config={}):

        x, y = [], []
        with open(self._get_abs_path(training_path), 'r') as f:
            for line in f:
                obj = json.loads(line)
                x.append(obj['feature_vector'])
                y.append(obj['label'])

        # train
        if len(x) == 0 or len(y) == 0 or len(x) != len(y):
            raise ValueError('Illegal training file')
        function = get_classifier_class(classifier)
        return function(**classifier_config).fit(x, y, **model_config)

    def dump_model(self, model, output_path):
        with open(self._get_abs_path(output_path), 'w') as f:
            f.write(pickle.dumps(model))

    def load_model(self, file_path):
        with open(self._get_abs_path(file_path), 'r') as f:
            return pickle.loads(f.read())

    def predict(self, model, feature_path, predict_output_path):

        with open(self._get_abs_path(predict_output_path), 'w') as output:
            with open(self._get_abs_path(feature_path), 'r') as input:
                for line in input:
                    obj = json.loads(line)
                    label = model.predict([obj['feature_vector']])
                    ret_dict = {
                        'id': obj['id'],
                        'label': label[0]
                    }
                    output.write(json.dumps(ret_dict))
                    output.write('\n')

    def set_root_path(self, root_path):
        """
        Set root path for relative paths in all configurations.

        Args:
            root_path (str): Root path for relative path.
        """
        self._root_path = os.path.abspath(root_path)

    def get_root_path(self):
        """
        Get current root path.

        Returns:
            str: Current root path.
        """
        return self._root_path

    def _get_abs_path(self, path):
        return path if os.path.isabs(path) else os.path.join(self._root_path, path)

    def get_file_iterator(self, file_path, *args, **kwargs):
        """
        Args:
            file_path (str): File path.
            type (str): It can be `json_line`, `text`, `csv`. \
                For `json_line` file, `id_path` should also be set. \
                For `text` file, id will be auto generated.
                For `csv` file, `id_column` should be set. \
                if there's no header, please set `column_names` (list).
        Returns:
            str, list: id, value list. \
                If the extracted id is a int, it will be convert to string with a 'int-' prefix,\
                for json line only supports string as key in object.
        """
        return FileIterator(file_path=self._get_abs_path(file_path), *args, **kwargs)

    def hamming_distance(self, s1, s2):
        """
        Hamming distance used to measure the minimum number of substitutions required to change one sequence into the
        other.

        Args:
            s1 (str or list): Sequence 1.
            s2 (str or list): Sequence 2.

        Returns:
            int: Hamming distance between two sequences.

        Examples:
            >>> tk.hamming_distance('ab','cd')
            2
            >>> tk.hamming_distance([1,2,3],[3,2,3])
            1
        """
        return hamming_distance(s1, s2)

    def hamming_similarity(self, s1, s2):
        """
        Hamming similarity is computed as 1 - normalized_hamming_distance.

        Args:
            s1 (str or list): Sequence 1.
            s2 (str or list): Sequence 2.

        Returns:
            float: Hamming similarity.

        Examples:
            >>> tk.hamming_similarity('ab','cd')
            0
            >>> tk.hamming_similarity([1,2,3],[3,2,3])
            0.666666666667
        """
        return hamming_similarity(s1, s2)

    def normalized_hamming_distance(self, s1, s2):
        """
        This normalized distance is computed as hamming distance divided by the maximum length of two sequences.

        Args:
            s1 (str or list): Sequence 1.
            s2 (str or list): Sequence 2.

        Returns:
            float: Normalized Hamming distance.
        """
        return normalized_hamming_distance(s1, s2)

    def levenshtein_similarity(self, s1, s2, name=None):
        """
        The Levenshtein similarity is computed as 1 - normalized_levenshtein_distance.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str): Name of resource (edit distance table). Defaults to None.

        Returns:
            float: Levenshtein Similarity.
        """
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
        """
        The Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str): Name of resource (edit distance table). Defaults to None.

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

    def normalized_levenshtein_distance(self, s1, s2, name=None):
        """
        This normalized distance is computed as levenshtein distance divided by the maximum cost of insertion from
        empty string to s1 or s2.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str): Name of resource (edit distance table). Defaults to None.

        Returns:
            float: Normalized Levenshtein Distance.
        """
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

    def optimal_string_alignment_distance(self, s1, s2):
        """
        This is a variation of the Damerau-Levenshtein distance that returns the strings' edit distance taking into account deletion, insertion, substitution, and transposition, under the condition that no substring is edited more than once.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Optimal String Alignment Distance.

        Examples:
            >>> rltk.optimal_string_alignment_distance('abcd', 'acbd')
            1
            >>> rltk.optimal_string_alignment_distance('ca', 'abc')
            3
        """
        return optimal_string_alignment_distance(s1, s2)    

    def needleman_wunsch_similarity(self, s1, s2, name=None, match=2, mismatch=-1, gap=-0.5):
        """
        This Needleman Wunsch Similarity is computed as needlman_wunsch_score over maximum score of s1 and s2.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            name (str, optional): Name of resource (alignment score matrix). Defaults to None.
            match (int, optional): Score of match.
            mismatch (int, optional): Score of mismatch.
            gap (int, optional): Gap penalty.

        Returns:
            float: Needleman Wunsch Similarity.
        """
        if name is None:
            return needleman_wunsch_similarity(s1, s2, match, mismatch, gap)
        else:
            self._has_resource(name, 'alignment_score_matrix')

            score_table = self._rs_dict[name]['data']
            return needleman_wunsch_similarity(s1, s2, match, mismatch, gap, score_table)

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
        return jaro_distance(s1, s2)

    def jaro_winkler_similarity(self, s1, s2, threshold=0.7, scaling_factor=0.1, prefix_len=4):
        """
        The max length for common prefix is 4.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            threshold (int, optional): Boost threshold, prefix bonus is only added \
                when compared strings have a Jaro Distance above it. Defaults to 0.7.
            scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards \
                for having common prefixes. Defaults to 0.1.
            prefix_len (int, optional): Length of common prefix. Defaults to 4.

        Returns:
            float: Jaro Winkler Similarity.

        Examples:
            >>> tk.jaro_winkler_similarity('abchello', 'abcworld')
            0.6833333333333332
            >>> tk.jaro_winkler_similarity('hello', 'world')
            0.4666666666666666
        """
        return jaro_winkler_similarity(s1, s2, threshold, scaling_factor, prefix_len)

    def jaro_winkler_distance(self, s1, s2, threshold=0.7, scaling_factor=0.1, prefix_len=4):
        """
        Jaro Winkler Distance is computed as 1 - jaro_winkler_similarity.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.
            threshold (int, optional): Boost threshold, prefix bonus is only added when compared strings have\
                a Jaro Distance above it. Defaults to 0.7.
            scaling_factor (int, optional): Scaling factor for how much the score is adjusted upwards\
                for having common prefixes. Defaults to 0.1.
            prefix_len (int, optional): Length of common prefix. Defaults to 4.

        Returns:
            float: Jaro Winkler Similarity.

        Examples:
            >>> tk.jaro_winkler_similarity('abchello', 'abcworld')
            0.6833333333333332
            >>> tk.jaro_winkler_similarity('hello', 'world')
            0.4666666666666666
        """
        return jaro_winkler_distance(s1, s2, threshold, scaling_factor, prefix_len)

    def dice_similarity(self, set1, set2):
        """
        The Dice similarity score is defined as twice the intersection of two sets divided by sum of lengths.

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.

        Returns:
            float: Dice similarity.

        Examples:
            >>> tk.dice_similarity(set(['a', 'b']), set(['c', 'b']))
            0.5
        """

        set1, set2 = utils.convert_list_to_set(set1), utils.convert_list_to_set(set2)
        return dice_similarity(set1, set2)

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

        set1, set2 = utils.convert_list_to_set(set1), utils.convert_list_to_set(set2)
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

        set1, set2 = utils.convert_list_to_set(set1), utils.convert_list_to_set(set2)
        return jaccard_index_distance(set1, set2)

    def hybrid_jaccard_similarity(self, set1, set2, threshold=0.5, function=None, parameters={}):
        """
        Generalized Jaccard Measure.

        Args:
            set1 (set): Set 1.
            set2 (set): Set 2.
            threshold (float, optional): The threshold to keep the score of similarity function. \
                Defaults to 0.5.
            function (function, optional): The reference of a similarity measure function. \
                It should return the value in range [0,1]. If it is set to None, \
                `jaro_winlker_similarity` will be used.
            parameters (dict, optional): Other parameters of function. Defaults to empty dict.

        Returns:
            float: Hybrid Jaccard similarity.

        Examples:
            >>> def hybrid_test_similarity(m ,n):
            ...     ...
            >>> tk.hybrid_jaccard_similarity(set(['a','b','c']), set(['p', 'q']), function=hybrid_test_similarity)
            0.533333333333
        """

        if not function:
            function = self.jaro_winkler_similarity

        set1, set2 = utils.convert_list_to_set(set1), utils.convert_list_to_set(set2)
        return hybrid_jaccard_similarity(set1, set2, threshold, function, parameters)

    def monge_elkan_similarity(self, bag1, bag2, function=None, parameters={}):
        """
        Monge Elkan similarity.

        Args:
            bag1 (list): Bag 1.
            bag2 (list): Bag 2.
            function (function, optional): The reference of a similarity measure function. \
                It should return the value in range [0,1]. If it is set to None, \
                `jaro_winlker_similarity` will be used.
            parameters (dict, optional): Other parameters of function. Defaults to empty dict.

        Returns:
            float: Monge Elkan similarity.
        """

        if not function:
            function = self.jaro_winkler_similarity
        return monge_elkan_similarity(bag1, bag2, function, parameters)

    def symmetric_monge_elkan_similarity(self, bag1, bag2, function=None, parameters={}):
        """
        Symmetric Monge Elkan similarity is computed by \
        (monge_elkan_similarity(b1, b2) + monge_elkan_similarity(b2, b1)) / 2.
        """

        if not function:
            function = self.jaro_winkler_similarity
        return symmetric_monge_elkan_similarity(bag1, bag2, function, parameters)

    def cosine_similarity(self, vec1, vec2):
        """
        The cosine similarity between to vectors.

        Args:
            vec1 (list): Vector 1. List of integer or float.
            vec2 (list): Vector 2. List of integer or float. It should have the same length to vec1.

        Returns:
            float: Cosine similarity.

        Examples:
            >>> tk.cosine_similarity([1, 2, 1, 3], [2, 5, 2, 3])
            0.916341933823
        """

        return cosine_similarity(vec1, vec2)

    def string_cosine_similarity(self, bag1, bag2):
        """
        The similarity between the two strings is the cosine of the angle between these two vectors representation.

        Args:
            bag1 (list): Bag1, tokenized string sequence.
            bag2 (list): Bag2, tokenized string sequence.

        Returns:
            float: Cosine similarity.
        """

        return string_cosine_similarity(bag1, bag2)

    def tf_idf_similarity(self, bag1, bag2, name, math_log=False):
        """
        Computes TF/IDF measure. This measure employs the notion of TF/IDF score commonly used in information retrieval (IR) to find documents that are relevant to keyword queries. The intuition underlying the TF/IDF measure is that two strings are similar if they share distinguishing terms.

        Args:
            bag1 (list): Bag 1.
            bag2 (list): Bag 2.
            name (str): Name of resource (document frequency corpus).
            math_log (bool, optional): Flag to indicate whether math.log() should be used in IDF formulas. \
                Defaults to False.

        Returns:
            float: TF/IDF similarity.

        Examples:
            >>> tk.tf_idf_similarity(['a','b','a'], ['a','c','d','f'], name='B1')
            0.17541160386140586
        """
        self._has_resource(name, 'df_corpus')
        return tf_idf_similarity(bag1, bag2, self._rs_dict[name]['data'], self._rs_dict[name]['docs_size'], math_log)

    def prep_df_corpus(self, name, math_log=False):
        self._check_valid_resource(name, 'df_corpus')
        df_corpus = self._get_df_corpus(name)

        # check if it needs to refresh
        if df_corpus['fresh'] is False:
            # compute idf
            df_corpus['idf'] = compute_idf(df_corpus['data'], df_corpus['docs_size'], math_log)

            # compute tfidf
            for doc_name, doc in df_corpus['docs'].iteritems():
                for t, tf in doc['tf'].iteritems():
                    doc['tf_idf'][t] = doc['tf'][t] * float(df_corpus['idf'][t])

            df_corpus['fresh'] = True

    def tf_idf_similarity_between_documents(self, corpus_name, doc_name1, doc_name2):
        self._check_valid_resource(corpus_name, 'df_corpus')
        df_corpus = self._get_df_corpus(corpus_name)
        return tf_idf_similarity_by_dict(
            df_corpus['docs'][doc_name1]['tf_idf'], df_corpus['docs'][doc_name2]['tf_idf'])

    def soundex_similarity(self, s1, s2):
        """
        The standard used for soundex implementation is provided by `U.S. Census Bureau <https://www.archives.gov/research/census/soundex.html>`_.
        soundex('ashcraft') == 'A261, soundex('pineapple') == 'P514'.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            int: 1 for same soundex code, 0 for different.

        Examples:
            >>> tk.soundex_similarity('ashcraft', 'pineapple')
            0
        """
        return soundex_similarity(s1, s2)

    def metaphone_similarity(self, s1, s2):
        """
        Metaphone fundamentally improves on the Soundex algorithm by using information about variations and inconsistencies in English spelling and pronunciation to produce a more accurate encoding, which does a better job of matching words and names which sound similar. As with Soundex, similar-sounding words should share the same keys. Metaphone is available as a built-in operator in a number of systems.
        metaphone('ashcraft') == 'AXKRFT', metaphone('pineapple') == 'PNPL'.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            int: 1 for same metaphone code, 0 for different.

        Examples:
            >>> tk.metaphone_similarity('ashcraft', 'pineapple')
            0
        """
        return metaphone_similarity(s1, s2)

    def nysiis_similarity(self, s1, s2):
        """
        New York State Immunization Information System (NYSIIS) Phonetic Code is a phonetic algorithm created by `The New York State Department of Health's (NYSDOH) Bureau of Immunization
        <https://www.health.ny.gov/prevention/immunization/information_system/>`_.
        metaphone('ashcraft') == 'AXKRFT', metaphone('pineapple') == 'PNPL'.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            int: 1 for same NYSIIS code, 0 for different.

        Examples:
            >>> tk.nysiis_similarity('ashcraft', 'pineapple')
            0
        """
        return nysiis_similarity(s1, s2)

    def longest_common_subsequence_distance(self, s1, s2):
        """
        The LCS distance between strings X (of length n) and Y (of length m) is n + m - 2 |LCS(X, Y)| min = 0 max = n + m

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Longest Common Subsequence Distance.

        Examples:
            >>> rltk.longest_common_subsequence_distance('abcd', 'acbd')
            2
            >>> rltk.longest_common_subsequence_distance('abcdefg', 'acef')
            3
        """ 
        return longest_common_subsequence_distance(s1, s2)

    def metric_longest_common_subsequence(self, s1, s2):
        """
        The Metric LCS distance between 2 strings is similar to LCS between 2 string where Metric Longest Common Subsequence is computed as 1 - |LCS(s1, s2)| / max(|s1|, |s2|)

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: Metric Longest Common Subsequence Distance.

        Examples:
            >>> rltk.longest_common_subsequence('ABCDEFG', 'ABCDEFHJKL')
            0.4
            # LCS: ABCDEF => length = 6
            # longest = s2 => length = 10
            # => 1 - 6/10 = 0.4

            >>> rltk.metric_longest_common_subsequence('ABDEF', 'ABDIF')
            4
            # LCS: ABDF => length = 4
            # longest = ABDEF => length = 5
            # => 1 - 4 / 5 = 0.2
        """
        return metric_longest_common_subsequence(s1, s2)

    def ngram_distance(self, s1, s2, n=2):
        """
        N-Gram Distance as defined by Kondrak, "N-Gram Similarity and Distance" String Processing and Information Retrieval, Lecture Notes in Computer Science Volume 3772, 2005, pp 115-126.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: NGram Distance.

        Examples:
            >>> rltk.ngram_distance('ABCD', 'ABTUIO')
            0.5833
        """
        return ngram_distance(s1, s2, n)

    def ngram_similarity(self, s1, s2, n=2):
        """
        N-Gram Similarity as defined by Kondrak, "N-Gram Similarity and Distance" String Processing and Information Retrieval, Lecture Notes in Computer Science Volume 3772, 2005, pp 115-126.

        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: NGram Similarity.

        Examples:
            >>> rltk.ngram_similarity('ABCD', 'ABTUIO')
            0.4166666666666667
        """
        return ngram_similarity(s1, s2, n)

    def qgram_distance(self, s1, s2, n=2):
        """
        QGram Distance is the number of distinct q-grams (n-grams) between 2 strings
        
        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: QGram Distance.

        Examples:
            >>> rltk.qgram_distance('abcde','abdcde')
            3
        """
        return qgram_distance(s1, s2, n)

    def qgram_similarity(self, s1, s2, n=2):
        """
        QGram Similarity is the number of common q-grams (n-grams) between 2 strings
        
        Args:
            s1 (str): Sequence 1.
            s2 (str): Sequence 2.

        Returns:
            float: QGram Similarity.

        Examples:
            >>> rltk.qgram_similarity('abcde','abdcde')
            3
        """
        return qgram_similarity(s1, s2, n)    

    def q_gram_blocking(self, output_file_path, **kwargs):
        """
        Q-Gram.

        Args:
            output_file_path (str): Output file string.
            iter1 (object): file iterator object
            q1 (str): qgram size
            value_path1 (str): value path of json
            iter2 (object, optional): file iterator object
            q2 (str, optional): qgram size
            value_path2 (str, optional): value path of json
            batch_size (str, optional): batch size of records to be indexed
            threshold (str, optional): threshold on block size
        """
        output_file_path = self._get_abs_path(output_file_path)
        kwargs['output_file_path'] = output_file_path
        return qgram_indexing(**kwargs)

    def canopy_blocking(self, iter1, output_file_path, iter2=None):
        """
        Canopy blocking.

        Args:
            iter1 (FileIterator): File iterator 1.
            iter2 (FileIterator, optional): File iterator 2. Defaults to None.
            output_file_path (str): Output file string.

        """
        output_file_path = self._get_abs_path(output_file_path)
        
    def lsh_minhash_blocking(self, output_file_path, **kwargs):
        """
        Minhash LSH based indexer. 

        Args:
            output_file_path (str): Output file string.
            iter1 (object): file iterator object
            value_path1 (str): value path of json
            iter2 (object, optional): file iterator object
            value_path2 (str, optional): value path of json
            batch_size (str, optional): batch size of records to be indexed
            num_perm (int, optional): The number of permutation functions used by the MinHash to be indexed. Default is 128.
            threshold (float, optional): The Jaccard similarity threshold between 0.0 and 1.0. The initialized MinHash LSH will be optimized for the threshold by minimizing the false positive and false negative. Default is 0.9.
            bands_rows (tuple(int,int), optional): The LSH parameters (i.e., number of bands and size of each bands). This is used to bypass the parameter optimization step in the constructor. threshold will be ignored if this is given.
        """
        output_file_path = self._get_abs_path(output_file_path)
        kwargs['output_file_path'] = output_file_path
        return minhash_lsh_indexing(**kwargs)

