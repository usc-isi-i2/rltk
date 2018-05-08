import os, json, time
import logging
from collections import defaultdict
from jsonpath_rw import parse

from rltk.tokenizer.digCrfTokenizer.crf_tokenizer import ngramTokenizer
from rltk.configuration import Configuration
import rltk.utils as utils

from datasketch import MinHash, MinHashLSH

class MinHashLSHRecordDeduplication(object):
    """
      Base Class to build Minhash LSH indexer for a single database. This class has methods to
      a) processes records in batches
      b) construct minhash lsh based signatures
      c) write minhash lsh indexes to disk
    """
    BATCH_SIZE = 20000
    NUM_PERMUTATIONS = 128
    THRESHOLD = 0.9
    INDEX_THRESHOLD = 1000
    BANDS = 0
    ROWS = 0
    QGRAM = 2
    
    _block_index = 0

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
        
        # MinHash LSH specific params
        if 'bands_rows' in self._kwargs:
            (self._bands, self._rows) = self._kwargs['bands_rows']
        else:
            (self._bands, self._rows) = (MinHashLSHRecordDeduplication.BANDS, MinHashLSHRecordDeduplication.ROWS)
        if 'num_perm' in self._kwargs:
            self._num_perm = int(self._kwargs['num_perm'])
        else:
            self._num_perm = MinHashLSHRecordDeduplication.NUM_PERMUTATIONS
        if 'threshold' in self._kwargs:
            self._threshold = float(self._kwargs['threshold'])
        else:
            self._threshold = MinHashLSHRecordDeduplication.THRESHOLD
        
        # Common params
        self.output_file_path = self._kwargs['output_file_path']
        self.value_path = self._kwargs['value_path1']
        self._discarded_indexes = set()
        self._file_iter = self._kwargs['iter1']
        
        if 'batch_size' in self._kwargs:
            self._batch_size = int(self._kwargs['batch_size'])
        else:
            self._batch_size = MinHashLSHRecordDeduplication.BATCH_SIZE

        self._erase_file_content(self.output_file_path)
        self.output_flag = False
        self.nt = ngramTokenizer()
        self._logger = logging.getLogger(Configuration.LOGGER_NAME)

    def _erase_file_content(self, file_path):
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

        # Common params
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
          2. update indexer by adding newly added block candidates and write to temp file
          Finally write back to original file and delete temp file

          Args:
            indexer (dict): Dictionary of block ID and corresponding record ids

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
                            if len(s) > MinHashLSHRecordDeduplication.INDEX_THRESHOLD:
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
                if len(v) < MinHashLSHRecordDeduplication.INDEX_THRESHOLD:
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
                    if len(v) < MinHashLSHRecordDeduplication.INDEX_THRESHOLD:
                        json.dump({k: v}, of)
                        of.write('\n')
                    else:
                        self._discarded_indexes.add(k)
            self.output_flag = True

    def _index_records(self, records):
        """
          Constructs Minhash LSH buckets for a given set of records

          Args:
            records (dict) : dict of (record_id -> record_value)

          Returns:
            None
        """
        indexer = defaultdict(list)
        
        # Create minhashes
        minhashes = {}
        for rid in records:
            m = MinHash(num_perm=self._num_perm)
            for d in records[rid]:
                qgrams = set(self.nt.basic(d, MinHashLSHRecordDeduplication.QGRAM))
                for gram in qgrams:
                    m.update(gram.encode('utf-8'))
            minhashes[rid] = m
        
        # Create LSH instance and add min hashes
        if self._bands == MinHashLSHRecordDeduplication.BANDS and self._rows == MinHashLSHRecordDeduplication.ROWS:
            lsh = MinHashLSH(threshold=self._threshold,num_perm=self._num_perm)
        else:
            lsh = MinHashLSH(num_perm=self._num_perm, params=(self._bands, self._rows))
            
        max_blocks = []
        for rid in records:
            lsh.insert(rid, minhashes[rid])
            max_blocks.append(rid)
        
        # Generate blocks
        while(len(max_blocks)>0):
            key = max_blocks[0]
            bucket = lsh.query(minhashes[key])
            for rid in bucket:
                if rid in max_blocks:
                    max_blocks.remove(rid)
                indexer["b"+str(self._block_index)].append(rid)
            self._block_index += 1
        
        self._write_indexer(indexer)

    def _build_index(self):
        """
          Builds MinHash LSH blocking indexer for single database. It processes records in batches of BATCH_SIZE.

          Args:
            None

          Returns:
            None
            Has a side effect of building MinHash LSH indexer and writing indexer to disk.
        """
        records = {}
        run_count = 0
        run_iteration = 1
        parse_dict = {}
        for k in self.value_path:
            parse_dict[k] = parse(k)
        for rid, json_data in self._file_iter:
            s = time.time()
            extracted_data = utils.extract(json_data, self.value_path, parse_dict)
            # Reset run_count when we hit BATCH_SIZE
            if run_count >= self._batch_size:
                self._index_records(records)
                msg = "Finished indexing {val} records. Time = {time}".format(val=run_count * run_iteration,time=(time.time() - s))
                self._logger.info('{0} {1}'.format("[minhash-lsh-blocking]", msg))

                run_iteration += 1
                records = {}
                run_count = 0

            records[rid] = set(extracted_data.values()[0])
            run_count += 1

        # Index the final remaining records
        if run_count > 0:
            self._index_records(records)
            msg = "Finished indexing {val} records. Time = {time}".format(val=run_count * run_iteration,time=(time.time() - s))
            self._logger.info('{0} {1}'.format("[minhash-lsh-blocking]", msg))

class MinHashLSHRecordLinkage(object):
    """
      Base Class to build Minhash LSH indexer for a multiple database. This class has methods to
      a) processes records in batches
      b) construct minhash lsh based signatures
      c) write minhash lsh indexes to disk
    """
    BATCH_SIZE = 50000
    NUM_PERMUTATIONS = 128
    THRESHOLD = 0.9
    INDEX_THRESHOLD = 1000
    BANDS = 0
    ROWS = 0
    QGRAM = 2

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
        
        # MinHash LSH specific params
        if 'bands_rows' in self._kwargs:
            (self._bands, self._rows) = self._kwargs['bands_rows']
        else:
            (self._bands, self._rows) = (MinHashLSHRecordLinkage.BANDS, MinHashLSHRecordLinkage.ROWS)
        if 'num_perm' in self._kwargs:
            self._num_perm = int(self._kwargs['num_perm'])
        else:
            self._num_perm = MinHashLSHRecordLinkage.NUM_PERMUTATIONS
        if 'threshold' in self._kwargs:
            self._threshold = float(self._kwargs['threshold'])
        else:
            self._threshold = MinHashLSHRecordLinkage.THRESHOLD
        
        # Common params
        self.output_file_path = self._kwargs['output_file_path']
        self.value_path1 = self._kwargs['value_path1']
        self.value_path2 = self._kwargs['value_path2']
        self._discarded_indexes = set()
        self._file_iter1 = self._kwargs['iter1']
        self._file_iter2 = self._kwargs['iter2']
        
        if 'batch_size' in self._kwargs:
            self._batch_size = int(self._kwargs['batch_size'])
        else:
            self._batch_size = MinHashLSHRecordLinkage.BATCH_SIZE

        self._erase_file_content(self.output_file_path)
        self.output_flag = False
        self.nt = ngramTokenizer()
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

        # Common params
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

    def _erase_file_content(self, file_path):
        if os.path.isfile(file_path) and os.stat(file_path).st_size > 0:
            open(self.output_file_path, 'w').close()

    def _write_indexer(self, indexer):
        """
          Writes indexer back to disk
          1. Read from indexer disk file if it exists
          2. update indexer by adding newly added block candidates and write to temp file
          Finally write back to original file and delete temp file

          Args:
            indexer (dict): Dictionary of block ID and corresponding record ids

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
                            if len(s) > MinHashLSHRecordLinkage.INDEX_THRESHOLD:
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
                if len(v) < MinHashLSHRecordLinkage.INDEX_THRESHOLD:
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
                    if len(v) < MinHashLSHRecordLinkage.INDEX_THRESHOLD:
                        json.dump({k: v}, of)
                        of.write('\n')
                    else:
                        self._discarded_indexes.add(k)
            self.output_flag = True

    def _index_records(self, records, key):
        """
          Constructs Minhash LSH buckets for a given set of records

          Args:
            records (dict) : dict of (record_id -> record_value)
            key (record_id) : record_id from first iterator which becomes a key

          Returns:
            None
        """
        indexer = defaultdict(list)
        
        # Create minhashes
        minhashes = {}
        for rid in records:
            m = MinHash(num_perm=self._num_perm)
            for d in records[rid]:
                qgrams = set(self.nt.basic(d, MinHashLSHRecordLinkage.QGRAM))
                for gram in qgrams:
                    m.update(gram.encode('utf-8'))
            minhashes[rid] = m
        
        # Create LSH instance and add min hashes
        if self._bands == MinHashLSHRecordLinkage.BANDS and self._rows == MinHashLSHRecordLinkage.ROWS:
            lsh = MinHashLSH(threshold=self._threshold,num_perm=self._num_perm)
        else:
            lsh = MinHashLSH(num_perm=self._num_perm, params=(self._bands, self._rows))
            
        for rid in records:
            lsh.insert(rid, minhashes[rid])

        bucket = lsh.query(minhashes[key])
        for rid in bucket:
            if key != rid:
                indexer[key].append(rid)
        
        self._write_indexer(indexer)

    def _build_index(self):
        """
          Builds MinHash LSH blocking indexer for single database. It processes records in batches of BATCH_SIZE.

          Args:
            None

          Returns:
            None
            Has a side effect of building MinHash LSH indexer and writing indexer to disk.
        """

        parse_dict1 = {}
        for k in self.value_path1:
            parse_dict1[k] = parse(k)

        parse_dict2 = {}
        for k in self.value_path2:
            parse_dict2[k] = parse(k)

        for rid1, json_data1 in self._file_iter1:

            records = {}
            run_count = 0
            run_iteration = 1
        
            # Key of the output index come from base iterator
            extracted_data1 = utils.extract(json_data1, self.value_path1, parse_dict1)
            records[rid1] = set(extracted_data1.values()[0])

            file_iter2_clone = self._file_iter2.copy()
            for rid2, json_data2 in file_iter2_clone:
                s = time.time()
                extracted_data2 = utils.extract(json_data2, self.value_path2, parse_dict2)
                
                # Reset run_count when we hit BATCH_SIZE
                if run_count >= self._batch_size:
                    self._index_records(records, rid1)
                    msg = "Finished indexing {val} records. Time = {time}".format(val=run_count * run_iteration,time=(time.time() - s))
                    self._logger.info('{0} {1}'.format("[minhash-lsh-blocking]", msg))

                    run_iteration += 1
                    records = {}
                    records[rid1] = set(extracted_data1.values()[0])
                    run_count = 0

                records[rid2] = set(extracted_data2.values()[0])
                run_count += 1

            # Index the final remaining records
            if run_count > 0:
                self._index_records(records, rid1)
                msg = "Finished indexing {val} records. Time = {time}".format(val=run_count * run_iteration,time=(time.time() - s))
                self._logger.info('{0} {1}'.format("[minhash-lsh-blocking]", msg))

def minhash_lsh_indexing(**kwargs):
    """
      Base interface to construct Minhash LSH indexes for databases.

      Args:
        **kwargs: Arbitrary keyword arguments

      Returns:
        None
        Has side effect of writing Minhash LSH indexes to file
    """
    if 'iter2' in kwargs:
        q = MinHashLSHRecordLinkage(**kwargs)
        q._build_index()
    else:
        q = MinHashLSHRecordDeduplication(**kwargs)
        q._build_index()
