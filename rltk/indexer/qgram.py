import os, json, time
import logging
from collections import defaultdict
from jsonpath_rw import parse

from rltk.tokenizer.digCrfTokenizer.crf_tokenizer import ngramTokenizer
from rltk.configuration import Configuration


class QgramRecordDeduplication(object):
    """
      Base Class to build Q gram indexer for a single database. This class has methods to
      a) processes records in batches
      b) construct q grams
      c) write q gram indexer to disk
    """
    BATCH_SIZE = 20000
    THRESHOLD_SIZE = 1000

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
        self._q = self._kwargs['q1']
        self.output_file_path = self._kwargs['output_file_path']
        self.value_path = self._kwargs['value_path1']
        self._discarded_indexes = set()
        self._file_iter = self._kwargs['iter1']

        if 'threshold' in self._kwargs:
            self._threshold = int(self._kwargs['threshold'])
        else:
            self._threshold = QgramRecordDeduplication.THRESHOLD_SIZE
        if 'batch_size' in self._kwargs:
            self._batch_size = int(self._kwargs['batch_size'])
        else:
            self._batch_size = QgramRecordDeduplication.BATCH_SIZE

        self.erase_file_content(self.output_file_path)
        self.output_flag = False
        self.nt = ngramTokenizer()
        self._logger = logging.getLogger(Configuration.LOGGER_NAME)

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
        if 'q1' not in kwargs:
            error_flag = True
            msg = 'Missing q argument- q'
        if 'output_file_path' not in kwargs:
            error_flag = True
            msg = 'Missing output file path argument - output_file_path'
        if 'value_path1' not in kwargs:
            error_flag = True
            msg = 'Missing blocking value path argument- value_path'
        if 'iter1' not in kwargs:
            error_flag = True
            msg = 'Missing file iterator argument - iter1'

        if error_flag:
            raise ValueError(msg)

    def _write_indexer(self, indexer):
        """
          Writes indexer back to disk
          1. Read from indexer disk file if it exists
          2. update indexer by adding current qgrams and write to temp file
          Finally write back to original file and delete temp file

          Args:
            indexer (dict): Dictionary of qgrams and corresponding record ids

          Returns:
            None
            Has a side effect of writing to output file
        """
        self.output_file_path = self._kwargs['output_file_path']

        if self.output_flag:
            filename, file_extension = os.path.splitext(self.output_file_path)
            temp_file = os.path.join(self.output_file_path + '.temp')
            temp_fptr = open(temp_file, 'w')
            with open(self.output_file_path, 'r') as of:
                for line in of:
                    jline = json.loads(line)
                    for k in jline.keys():
                        # merge qgram indexes if they already exist
                        if k in indexer:
                            s = set(jline[k])
                            s |= set(indexer[k])
                            # check if length of qgram indexes threshold size
                            if len(s) > self._threshold:
                                self._discarded_indexes.add(k)
                            if k not in self._discarded_indexes:
                                json.dump({k: list(s)}, temp_fptr)
                                temp_fptr.write('\n')

                            # we have already seen key k
                            del indexer[k]
                        else:
                            json.dump(jline, temp_fptr)
                            temp_fptr.write('\n')

            # Write remaining indexes to temp file
            for k, v in indexer.items():
                if len(v) < self._threshold:
                    json.dump({k: v}, temp_fptr)
                    temp_fptr.write('\n')
                else:
                    self._discarded_indexes.add(k)
            temp_fptr.close()

            # write back temp file to output file line by line (less memory)
            op_fptr = open(self.output_file_path, 'w')
            with open(temp_file, 'r') as tf:
                for line in tf:
                    jline = json.loads(line)
                    json.dump(jline, op_fptr)
                    op_fptr.write('\n')
            op_fptr.close()
            # delete temp file
            os.remove(temp_file)
        else:
            # Writing to output file for first time
            with open(self.output_file_path, 'w') as of:
                for k, v in indexer.items():
                    if len(v) < self._threshold:
                        json.dump({k: v}, of)
                        of.write('\n')
                    else:
                        self._discarded_indexes.add(k)
            self.output_flag = True

    def _index_records(self, records):
        """
          Constructs qgrams for a given set of records

          Args:
            records (list) : list of tuples of the form (record_id, record_value)

          Returns:
            None
        """
        indexer = defaultdict(list)
        for record in records:
            blocking_value = record[1]

            for b_value in blocking_value:
                for ngram_size in self._q:
                    qgrams = self.nt.basic(b_value, ngram_size)
                    for gram in qgrams:
                        indexer[gram].append(record[0])
        self._write_indexer(indexer)

    def build_index(self):
        """
          Builds Q gram blocking indexer for single database. It processes records in batches of BATCH_SIZE.

          Args:
            None

          Returns:
            None
            Has a side effect of building qgrams and writing indexer to disk.
        """
        records = []
        run_count = 0
        run_iteration = 1
        parse_dict = {}
        for k in self.value_path:
            parse_dict[k] = parse(k)
        s = time.time()
        for rid, json_data in self._file_iter:
            extracted_data = extract(json_data, self.value_path, parse_dict)
            # Reset run_count when we hit BATCH_SIZE
            if run_count >= self._batch_size:
                self._index_records(records)
                msg = "Finished indexing {val} records. Time = {time}".format(val=run_count * run_iteration,
                                                                              time=(time.time() - s))
                self._logger.info('{0} {1}'.format("[qgram-blocking]", msg))

                run_iteration += 1
                records = []
                run_count = 0

            records.append((rid, extracted_data.values()))
            run_count += 1

        # Index the final remaining records
        self._index_records(records)

    def get_inverted_index(self):
        """
          Builds inverted index from the index file

          Args:
            None

          Returns:
            dict: {record_id: [qgrams]}
        """
        inverted_index = defaultdict(list)
        with open(self.output_file_path, 'r') as ip:
            for line in ip:
                jline = json.loads(line)
                for k in jline.keys():
                    id_list = jline[k]
                    for id_v in id_list:
                        inverted_index[id_v].append(k)

        return inverted_index

    def get_index(self):
        """
          Builds index from index file

          Args:
            None

          Returns:
            dict: {qgram: [record_ids]}
        """
        index = defaultdict(list)
        with open(self.output_file_path, 'r') as ip:
            for line in ip:
                jline = json.loads(line)
                for k in jline.keys():
                    index[k].extend(jline[k])

        return index


class QgramRecordLinkage(object):
    """
      Base Class to build Q gram indexer for a multiple databases.
    """

    def __init__(self, **kwargs):
        """
          Initializer to setup variables
        """

        self._check_args(kwargs)
        self._kwargs = kwargs
        self._first_db_kwargs = {'q1': kwargs['q1'], 'value_path1': kwargs['value_path1'],
                                 'iter1': kwargs['iter1']}
        self._second_db_kwargs = {'q1': kwargs['q2'], 'value_path1': kwargs['value_path2'],
                                  'iter1': kwargs['iter2']}
        self.output_file_path = self._kwargs['output_file_path']
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
        if 'q1' not in kwargs:
            error_flag = True
            msg = 'Missing q1 argument- q1'
        if 'q2' not in kwargs:
            error_flag = True
            msg = 'Missing q1 argument- q2'
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
        if os.path.isfile(file_path) and os.stat(file_path).st_size > 0:
            open(self.output_file_path, 'w').close()

    def _write_result(self, opfile, results):
        """
          Write results to output file
          Args:
            opfile(string) : file path of output file
            results(list) : list of json records
        """
        with open(self.output_file_path, 'a') as ofile:
            for r in results:
                json.dump(r, ofile)
                ofile.write('\n')

    def build_index(self):
        """
          Builds Qgram indexer for two databases. It first constructs indexes for individual databases and then combines them

          Args:
            None

          Returns:
            None
            Has a side effect of writing indexer to output file
        """
        self._logger.info('{0} {1}'.format("[qgram-blocking]", "started building index for first database..."))
        s = time.time()
        q1 = QgramRecordDeduplication(**self._first_db_kwargs)
        q1.build_index()
        e = time.time()
        msg = "Finished building indexes for first database. Time taken: {0} s".format(str(e - s))
        self._logger.info('{0} {1}'.format("[qgram-blocking]", msg))

        q2 = QgramRecordDeduplication(**self._second_db_kwargs)
        q2.build_index()

        t = time.time()
        msg = "Finished building indexes for second database. Time taken: {0} s".format(str(t - e))
        self._logger.info('{0} {1}'.format("[qgram-blocking]", msg))
        q1_inverted_index = q1.get_inverted_index()
        q2_index = q2.get_index()

        # If output file has some contents, rewrite it
        self.erase_file_content(self.output_file_path)

        results = []
        # This will append indexes to the output file
        for k, v in q1_inverted_index.items():
            candidate_set = set()
            for id_p in v:
                candidate_set |= set(q2_index[id_p])

            if len(candidate_set) > 0:
                results.append({k: list(candidate_set)})

            if len(results) > QgramRecordDeduplication.BATCH_SIZE:
                self._write_result(self.output_file_path, results)
                results = []

        if len(results) > 0:
            self._write_result(self.output_file_path, results)
            results = []
        k = time.time()

        msg = "Finished building combined indexes. Time taken: {0} s".format(str(k - t))
        self._logger.info('{0} {1}'.format("[qgram-blocking]", msg))

        os.remove(self._first_db_kwargs['output_file_path'])
        os.remove(self._second_db_kwargs['output_file_path'])


def qgram_indexing(**kwargs):
    """
      Base interface to construct Qgram indexes for databases.

      Args:
        **kwargs: Arbitrary keyword arguments

      Returns:
        None
        Has side effect of writing Qgram indexes to file
    """
    if 'iter2' in kwargs:
        q = QgramRecordLinkage(**kwargs)
        q.build_index()
    else:
        q = QgramRecordDeduplication(**kwargs)
        q.build_index()
