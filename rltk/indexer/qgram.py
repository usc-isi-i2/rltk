import sys, os, json
from collections import defaultdict

from ..tokenizer.digCrfTokenizer.crf_tokenizer import ngramTokenizer
from ..similarity.jaccard import jaccard_index_distance as jd
from ..file_iterator import FileIterator
from utils import extract

"""
  Base Class to build Q gram indexer for a single database. This class has methods to
  a) processes records in batches 
  b) construct q grams
  c) write q gram indexer to disk
"""
class QgramRecordDeduplication(object):
  BATCH_SIZE = 1000
  THRESHOLD_SIZE = 1000

  """
    Initialiser to setup variables

    Args:
      kwargs(dict): dictionary of argument key value pairs

    Returns:
      None
  """
  def __init__(self, **kwargs):
    self._check_args(kwargs)
    self._kwargs = kwargs
    self.q = self._kwargs['q']
    self.output_file_path = self._kwargs['output_file_path']
    self.value_path = self._kwargs['value_path']

    if 'threshold' in self._kwargs:
      self.threshold = int(self._kwargs['threshold'])
    else:
      self.threshold = QgramRecordDeduplication.THRESHOLD_SIZE
    if 'batch_size' in self._kwargs:
      self.batch_size = int(self._kwargs['batch_size'])
    else:
      self.batch_size = QgramRecordDeduplication.BATCH_SIZE

  """
    Helper method to check if 
    a) necessary arguments are passed
    b) Argument values are of correct (value / type) 

    Args:
      kwargs (dict): Dictionary of argument key value pairs

    Returns:
      None

  """
  def _check_args(self, kwargs):
    error_flag = False
    if 'q' not in kwargs:
      error_flag = True
      msg = 'Missing q argument- q'
    if 'output_file_path' not in kwargs:
      error_flag = True
      msg = 'Missing output file path argument - output_file_path'
    if 'file_iter1' not in kwargs:
      error_flag = True
      msg = 'Missing file iterator argument - file_iter1'
    if 'value_path' not in kwargs:
      error_flag = True
      msg = 'Missing blocking value path argument- value_path'

    if error_flag:
      raise ValueError(msg)

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
  def _write_indexer(self, indexer):
    self.output_file_path = self._kwargs['output_file_path']

    # If output file exists and not empty
    if os.path.isfile(self.output_file_path) and os.stat(self.output_file_path).st_size != 0:      
      filename, file_extension = os.path.splitext(self.output_file_path)
      temp_file = os.path.join(self.output_file_path + '.temp')
      temp_fptr = open(temp_file, 'w')
      with open(self.output_file_path, 'r') as of:
        for line in of:
          jline = json.loads(line)
          k = jline.keys()[0]
          if k in indexer:
            s = set(jline[k])
            s |= set(indexer[k])
            json.dump({k: list(s)}, temp_fptr)
            temp_fptr.write('\n')
          else:
            json.dump(jline, temp_fptr)
            temp_fptr.write('\n')
      temp_fptr.close()

      #write back temp file to output file line by line (less memory)
      op_fptr = open(self.output_file_path, 'w')
      with open(temp_file, 'r') as tf:
        for line in tf:
          jline = json.loads(line)
          json.dump(jline, op_fptr)
          op_fptr.write('\n')
      op_fptr.close()

      #delete temp file
      os.remove(temp_file)
    else:
      #Writing to output file for first time
      with open(self.output_file_path, 'w') as of:
        for k,v  in indexer.items():
          json.dump({k: list(v)}, of)
          of.write('\n')

  """
    Constructs qgrams for a given set of records

    Args:
      records (list) : list of tuples of the form (record_id, record_value)

    Returns:
      None
  """
  def _index_records(self, records):
    nt = ngramTokenizer()
    indexer = defaultdict(set)
    for record in records:
      blocking_value = record[1]
      qgrams = []
      for bv in blocking_value:
        for ngram_size in self.q:
          qgrams.extend(nt.basic(bv, ngram_size))

      for gram in qgrams:
        indexer[gram].add(record[0])

    self._write_indexer(indexer)

  """
    Builds Q gram blocking indexer for single database. It processes records in batches of BATCH_SIZE.

    Args:
      None

    Returns:
      None
      Has a side effect of building qgrams and writing indexer to disk.
  """
  def build_index(self):
    file_iterator = self._kwargs['file_iter1']
    records = []
    run_count = 0
    for rid, json_data in file_iterator:
      extracted_data = extract(json_data, self.value_path)
      #Reset run_count when we hit BATCH_SIZE
      if run_count >= QgramRecordDeduplication.BATCH_SIZE:
        self._index_records(records)
        records = []
        run_count = 0

      records.append((rid, extracted_data.values()))
      run_count += 1

    #Index the final remaining records
    self._index_records(records)

"""
  Base Class to build Q gram indexer for a multiple databases.
"""
class QgramRecordLinkage(object):
  def __init__(self, **kwargs):
    self._kwargs = kwargs


def qgram_indexing(**kwargs):
  if 'file_iter2' in kwargs:
    q1 = QgramRecordDeduplication(**kwargs)
    q1.build_index()
    q2 = QgramRecordDeduplication(**kwargs)
    q2.build_index()
  else:
    q = QgramRecordDeduplication(**kwargs)
    q.build_index()



