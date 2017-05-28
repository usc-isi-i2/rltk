import sys, os, json, time, random,logging
from random import shuffle
from collections import defaultdict
from jsonpath_rw import parse

from rltk.tokenizer.digCrfTokenizer.crf_tokenizer import ngramTokenizer
from rltk.similarity.jaccard import jaccard_index_distance as jd
from rltk.file_iterator import FileIterator
from rltk.configuration import Configuration
from qgram import QgramRecordDeduplication as qd
from utils import extract


class CanopyRecordDeduplication(object):
    """
        Base Class for canopy indexer single database deduplication
    """
    def __init__(self, **kwargs):
        """
        """
        self._check_args(kwargs)
        self._similarity = self._kwargs['similarity']
        self._t1 = self._kwargs['t1']
        self._t2 = self._kwargs['t2']
        self._tokeniser = {'type': self._kwargs['token_params']['token_type'], 'ngram': self._kwargs['token_params']['n']}
        self.output_file_path = self._kwargs['output_file_path']
        self._logger = logging.getLogger(Configuration.LOGGER_NAME)


class CanopyRecordLinkage(object):
    """
        Base Class to build canopy indexer
    """
    def __init__(self, **kwargs):
        """
          Initialiser to setup variables

          Args:
          **kwargs: Arbitrary keyword arguments

          Returns:
            None
        """
        self._check_args(kwargs)
        self._kwargs = kwargs
        self._similarity = self._kwargs['similarity']
        self._t1 = self._kwargs['t1']
        self._t2 = self._kwargs['t2']
        self._tokeniser = {'type': self._kwargs['token_params']['token_type'], 'ngram': self._kwargs['token_params']['n']}
        self.output_file_path = self._kwargs['output_file_path']

        self._first_db_kwargs = {'q1': self._kwargs['token_params']['n'], 'value_path1': kwargs['value_path1'], 'iter1': kwargs['iter1']}
        self._second_db_kwargs = {'q1': self._kwargs['token_params']['n'], 'value_path1': kwargs['value_path2'], 'iter1': kwargs['iter2']}
        filename, file_extension = os.path.splitext(self.output_file_path)

        first_db_output_path = os.path.join(filename + '_first_db.jsonl')
        self.erase_file_content(first_db_output_path)
        second_db_output_path = os.path.join(filename + '_second_db.jsonl')
        self.erase_file_content(second_db_output_path)
        self._first_db_kwargs['output_file_path'] = first_db_output_path
        self._second_db_kwargs['output_file_path'] = second_db_output_path
        self._logger = logging.getLogger(Configuration.LOGGER_NAME)


    def _check_args(self, kwargs):
        """
          Helper method to check if
          a) necessary arguments are passed
          b) Argument values are of correct (value / type)

          Args:
            kwargs (dict): Dictionary of argument key value pairs

          Returns:
            None
        """
        error_flag = False
        if 't1' not in kwargs:
            error_flag = True
            msg = 'Missing t1 argument- t1'
        if 't2' not in kwargs:
            error_flag = True
            msg = 'Missing q1 argument- t2'
        if 'output_file_path' not in kwargs:
            error_flag = True
            msg = 'Missing output file path argument - output_file_path'
        if 'value_path1' not in kwargs:
            error_flag = True
            msg = 'Missing blocking value path argument- value_path1'
        if 'value_path2' not in kwargs:
            error_flag = True
            msg = 'Missing blocking value path argument- value_path2'
        if 'iter1' not in kwargs:
            error_flag = True
            msg = 'Missing file iterator argument - iter1'
        if 'iter2' not in kwargs:
            error_flag = True
            msg = 'Missing file iterator argument - iter2'

        if error_flag:
            raise ValueError(msg)

    def erase_file_content(self, file_path):
        """
          This erases file contents if the file exists.

          Args:
            file_path(string) : file path

          Returns:
            None
        """
        if os.path.isfile(file_path) and os.stat(file_path).st_size > 0:
            open(self.output_file_path, 'w').close()

    def get_distance_metric(self, r1, r2, similarity):
        """
            Get distance measure between two records

            Args:
                r1(list) : first_record
                r2(list) : second record
                similarity(string): similarity measure {jaccard}
        """
        if self.is_similarity_jaccard(similarity):
            #Optimised version of Jaccard
            #a) Use Demorgan's law to calculate len of union from individual sets and their intersection
            #b) Instead of calculating Jaccard distance and check for thresholds, 
            #    optimize (1 - u/d) < thresholds to remove floating poitnt divisions. Saves around ~60s of computation on 100k records.
            s1,s2 = r1, r2
            if type(r1) == list:
                s1 = set(r1)
            if type(r2) == list:
                s2 = set(r2)
            s3 = s1.intersection(s2)
            intersection_len = len(s3)
            union_len = (len(s1) + len(s2) - intersection_len)

            if (union_len - intersection_len) < (self._t1 * union_len):
                if (union_len - intersection_len) < (self._t2 * union_len):
                    return (True, True)
                else:
                    return (True, False)
            else:
                return (False,False)

    def is_similarity_jaccard(self, similarity):
        """
            Helper function to check if similarity measure is jaccard

            Args:
                similarity(string) : jaccard
        """
        return similarity == "jaccard"

    def write_output(self, records):
        """
            Write output records to file

            Args:
                records(list) : records to be written to file
        """
        with open(self.output_file_path , 'a') as ofile:
            for record in records:
                json.dump( record, ofile)
                ofile.write('\n')

    def build_index(self):
        """
          Builds Canopy indexer for multiple databases.

          Args:
            None

          Returns:
            None
            Has a side effect of building canopies and writing indexer to disk.
        """
        s = time.time()
        msg = "Starting canopy indexer..."
        self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))
        r1 = qd(**self._first_db_kwargs)
        r1.build_index()

        msg = "Finished building qgrams for first database. Time = {time}".format(time=(time.time() - s))
        self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))
        r2 = qd(**self._second_db_kwargs)
        r2.build_index()
        msg = "Finished building qgrams for second database. Time = {time}".format(time=(time.time() - s))
        self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))

        r1_inv_index = r1.get_inverted_index()
        r2_inv_index = r2.get_inverted_index()
        r2_index = r2.get_index()

        record_size = len(r1_inv_index)
        r2_record_size = len(r2_inv_index)
        r1_record_size = len(r1_inv_index)

        msg = "Started building canopies. Time = {time}".format(time=(time.time() - s))
        self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))

        r1_keys = r1_inv_index.keys()
        shuffle(r1_keys)
        count = 0
        batch = 2000
        batch_result = []
        for r1_record in r1_keys:
            count += 1
            candidate_set = set()
            for id_p in r1_inv_index[r1_record]:
              candidate_set |=  set(r2_index[id_p])

            canopy_candidates = []
            for c in candidate_set:
                candidate, adjacent_candidate = self.get_distance_metric(r1_inv_index[r1_record], r2_inv_index[c], self._similarity)

                if candidate:
                    canopy_candidates.append(c)
                    #Remove all points which are within the tight threshold
                    if adjacent_candidate:
                        del r2_inv_index[c]

            if len(canopy_candidates) > 0:
                batch_result.append({r1_record: canopy_candidates})

            if count % batch == 0:
                self.write_output(batch_result)
                msg = "Finished indexing {total} records. Time = {time}".format(total=count, time=(time.time() - s))
                self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))
                batch_result = []

        if len(batch_result) > 0:
            self.write_output(batch_result)

        msg = "Finished building canopy indexer. Time = {time}".format(time=(time.time() - s))
        self._logger.info('{0} {1}'.format("[canopy-blocking]", msg))

def canopy_indexing(**kwargs):
    """
      Base interface to construct Canopy indexes for databases.

      Args:
        **kwargs: Arbitrary keyword arguments

      Returns:
        None
    """
    if 'iter2' in kwargs:
        cp = CanopyRecordLinkage(**kwargs)
        cp.build_index()
    else:
        #cp = CanopyRecordDeduplication(**kwargs)
        #cp.build_index()
        pass
