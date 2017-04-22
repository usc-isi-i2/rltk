import sys, os, json, fileinput
from collections import defaultdict

from jsonpath_rw import parse
from jsonpath_rw.jsonpath import Fields

#Fix later - add relative import
#sys.path.append('/home/chinmay/CODE/ISI/toolkit/rltk/rltk/tokenizer/digCrfTokenizer')
#from ..tokeniser.digCrfTokenizer import ngramTokenizer as nt
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../tokenizer/digCrfTokenizer")))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../similarity")))
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../")))
from crf_tokenizer import ngramTokenizer
from jaccard import jaccard_index_distance as jd
from file_iterator import FileIterator


class QgramRecordLinkage(object):
  def __init__(self, **kwargs):
    self._kwargs = kwargs

class QgramRecordDeduplication(object):
  BATCH_SIZE = 1000

  #TO-DO Check if arguments are present
  def __init__(self, **kwargs):
    self._kwargs = kwargs
    self.q = self._kwargs['q']
    self.threshold = None
    if 'threshold' in self._kwargs:
      self.threshold = int(self._kwargs['threshold'])

  '''
    1. Read from indexer file 
    2. update indexer by adding current qgrams and write to temp file
     
    Finally write back to original file and delete temp file
  '''
  def _write_indexer(self, indexer):
    op_file = self._kwargs['output_file_path']

    # If output file exists and not empty
    if os.path.isfile(op_file) and os.stat(op_file).st_size != 0:      
      filename, file_extension = os.path.splitext(op_file)
      temp_file = os.path.join(op_file + '.temp')
      temp_fptr = open(temp_file, 'w')
      with open(op_file, 'r') as of:
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
      op_fptr = open(op_file, 'w')
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
      with open(op_file, 'w') as of:
        for k,v  in indexer.items():
          json.dump({k: list(v)}, of)
          of.write('\n')

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

  '''
    Process records in batches of BATCH_SIZE
  '''
  def build_index(self):
    file_iterator = self._kwargs['iter1']
    records = []
    run_count = 0
    for rid, value in file_iterator:
      #Reset run_count when we hit BATCH_SIZE
      if run_count >= QgramRecordDeduplication.BATCH_SIZE:
        self._index_records(records)
        records = []
        run_count = 0

      records.append((rid,value))
      run_count += 1

    #Index the final remaining records
    self._index_records(records)

def qgram_indexing(**kwargs):
  if 'iter2' in kwargs:
    q = QgramRecordLinkage(**kwargs)
  else:
    q = QgramRecordDeduplication(**kwargs)
    q.build_index()



