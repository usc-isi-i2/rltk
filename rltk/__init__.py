<<<<<<< HEAD
<<<<<<< HEAD
from .evaluation import *
# from .indexer import *
# from .similarity import *
# from .tokenizer import *
# from .core import *
# from .record import Record
# from .record_iterator import RecordIterator
=======
from rltk.record import Record
from rltk.dataset import Dataset, get_record_pairs
from rltk.io import *
from rltk.similarity import *
>>>>>>> usc-isi-i2/v2
=======
from rltk.record import Record, cached_property, generate_record_property_cache, validate_record
from rltk.dataset import Dataset, get_record_pairs
from rltk.io import *
from rltk.similarity import *
from rltk.blocking import *
>>>>>>> usc-isi-i2/v2
