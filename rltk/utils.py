import unicodedata

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rltk.dataset import Dataset
    from rltk.io.reader.block_reader import BlockReader
    from rltk.evaluation.ground_truth import GroundTruth


def check_for_none(*args):
    for arg in args:
        if arg is None:
            raise ValueError('Missing parameter')


def check_for_type(type, *args):
    for arg in args:
        if not isinstance(arg, type):
            raise TypeError('Wrong type of parameter')


def unicode_normalize(s):
    return unicodedata.normalize('NFKD', s)


def convert_list_to_set(s):
    if isinstance(s, list):
        s = set(s)
    return s


def get_record_pairs(dataset1: 'Dataset',
                     dataset2: 'Dataset',
                     block_reader: 'BlockReader' = None,
                     ground_truth: 'GroundTruth' = None):
    """
    Generate pairs to compare.

    Args:
        dataset1 (Dataset): dataset 1
        dataset2 (Dataset): dataset 2
        block_reader (BlockReader, optional): block reader
        ground_truth (GroundTruth, optional): ground truth
    """
    if block_reader and not ground_truth:
        for _, id1, id2 in block_reader:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    elif ground_truth and not block_reader:
        for id1, id2, label in ground_truth:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    elif ground_truth and block_reader:
        for _, id1, id2 in block_reader:
            if ground_truth.is_member(id1, id2):
                yield dataset1.get_record(id1), dataset2.get_record(id2)
    else:
        for r1 in dataset1:
            for r2 in dataset2:
                yield r1, r2
