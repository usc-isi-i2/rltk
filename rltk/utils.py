import unicodedata
import warnings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rltk.dataset import Dataset
    from rltk.blocking.block import Block
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


def get_record_pairs(dataset1,
                     dataset2,
                     block: 'Block' = None,
                     ground_truth: 'GroundTruth' = None):
    """
    Generate pairs to compare.

    Args:
        dataset1 (Dataset): dataset 1
        dataset2 (Dataset): dataset 2
        block (Block, optional): block 
        ground_truth (GroundTruth, optional): ground truth
    """
    if block and not ground_truth:
        for _, id1, id2 in block.pairwise(dataset1.id, dataset2.id):
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    elif ground_truth and not block:
        for id1, id2, label in ground_truth:
            yield dataset1.get_record(id1), dataset2.get_record(id2)
    elif ground_truth and block:
        for _, id1, id2 in block.pairwise(dataset1.id, dataset2.id):
            if ground_truth.is_member(id1, id2):
                yield dataset1.get_record(id1), dataset2.get_record(id2)
    else:
        for r1 in dataset1:
            for r2 in dataset2:
                yield r1, r2


def module_importer(module_names: str, dependencies: str, notes: str = None):
    if isinstance(dependencies, str):
        dependencies = [dependencies]

    def module():
        try:
            return __import__(module_names)
        except ImportError:
            warning_msg = '\n-----------------------------------\n'
            warning_msg += '\nImport Dependencies Error\n'

            if len(dependencies) > 0:
                warning_msg += '\nPlease install dependencies:\n'
                for d in dependencies:
                    warning_msg += d + '\n'

            if notes:
                warning_msg += notes

            warning_msg += '\n-----------------------------------'
            warnings.warn(warning_msg)
            exit(500)

    return module
