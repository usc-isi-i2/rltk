from rltk.record import Record, cached_property, generate_record_property_cache, validate_record, remove_raw_object
from rltk.dataset import Dataset
from rltk.io import *
from rltk.similarity import *
from rltk.blocking import *
from rltk.tokenizer import *
from rltk.evaluation import *


def get_record_pairs(dataset1: Dataset, dataset2: Dataset,
                     block_reader: BlockReader = None,
                     ground_truth: GroundTruth = None):
    """
    Generate pairs to compare.

    Args:
        dataset1 (Dataset): dataset 1
        dataset2 (Dataset): dataset 2
        block_reader (BlockReader, optional): block reader
        ground_truth (GroundTruth, optional): ground truth
    """
    if block_reader:
        for id1, id2 in block_reader:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    elif ground_truth:
        for id1, id2, label in ground_truth:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    else:
        for r1 in dataset1:
            for r2 in dataset2:
                yield r1, r2
