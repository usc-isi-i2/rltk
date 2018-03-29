import pytest

from rltk.record import Record
from rltk.evaluation.ground_truth import GroundTruth
from rltk.evaluation.trial import Trial
from rltk.evaluation.evaluation import Evaluation
from rltk.similarity import *


class TestRecord(Record):
    @property
    def id(self):
        return self.raw_object['id']

    @property
    def data(self):
        print('123', self.raw_object)
        return self.raw_object['data']


@pytest.mark.parametrize('ground_truth_list, cal_result_list, min_c, top_k,tp,tn,fp,fn', [
    ([(1, 1, 10, 0, True), (2, 2, 11, 0, True), (3, 1, 12, 1, False), (4, 2, 13, 1, False)],
     [(1, 1, 10, 0, True, 0.5), (2, 2, 11, 0, False, 0.5), (3, 1, 12, 1, True, 0.5), (4, 2, 13, 1, False, 0.5)], 0, 0,
     0.5, 0.5, 0.5,
     0.5),
    # ([(1, 0, True), (2, 0, True), (1, 1, False), (2, 1, False)],
    #  [(1, 0, True, 0.6), (2, 0, False, 0.5), (1, 1, True, 0.5), (2, 1, False, 0.6)], 0, 2, 1.0, 1.0, 0, 0)
])
def test_basic(ground_truth_list, cal_result_list, min_c, top_k, tp, tn, fp, fn):
    # if not isinstance(ground_truth_list, (list)) or not isinstance(cal_result_list, (list)):
    #     with pytest.raises(ValueError):
    # # number_equal(n1, n2)
    # else:
    do_test_trial(ground_truth_list, cal_result_list, min_c, top_k, tp, tn, fp, fn)


def do_test_trial(ground_truth_list, cal_result_list, min_c, top_k, tp, tn, fp, fn):
    gt = GroundTruth()

    for r1_id, r1_d, r2_id, r2_d, p in ground_truth_list:
        raw_object = {'id': r1_id, 'data': r1_d}
        r1 = TestRecord(raw_object)
        raw_object = {'id': r2_id, 'data': r2_d}
        r2 = TestRecord(raw_object)
        gt.add_ground_truth(r1_id, r2_id, p)

    trial = Trial(gt, min_c, top_k)
    for r1_id, r1_d, r2_id, r2_d, p, c in cal_result_list:
        raw_object = {'id': r1_id, 'data': r1_d}
        r1 = TestRecord(raw_object)
        raw_object = {'id': r2_id, 'data': r2_d}
        r2 = TestRecord(raw_object)
        trial.add_result(r1, r2, p, c)

    eva = Evaluation()
    eva.add_trial(trial)

    assert eva.true_positives() == tp
    assert eva.true_negatives() == tn
    assert eva.false_positives() == fp
    assert eva.false_negatives() == fn


@pytest.mark.parametrize('ground_truth_list, min_c, top_k, similarity_info, tp, tn, fp, fn', [
    ([('0', '', '10', 'abc', False), ('1', 'abc', '11', 'abc', True), ('2', 'abcd', '12', 'abc', False),
      ('3', 'abd', '13', 'abc', False)],
     0, 0, [('levenshtein_similarity', 0.9), ('string_equal', 0.5)], 1.0, 1.0, 0, 0),
    ([('0', '', '10', 'abc', False), ('1', 'abc', '11', 'abc', True), ('2', 'abcd', '12', 'abc', False),
      ('3', 'abd', '13', 'abc', False)],
     0, 3, [('levenshtein_similarity', 0.9), ('string_equal', 0.5)], 1.0, 1.0, 0, 0)
])
def test_lvl(ground_truth_list, min_c, top_k, similarity_info, tp, tn, fp, fn):
    gt = GroundTruth()

    for r1_id, r1_d, r2_id, r2_d, p in ground_truth_list:
        raw_object = {'id': r1_id, 'data': r1_d}
        r1 = TestRecord(raw_object)
        raw_object = {'id': r2_id, 'data': r2_d}
        r2 = TestRecord(raw_object)
        gt.add_ground_truth(r1_id, r2_id, p)

    for similarity_function, min_confidence in similarity_info:
        trial = Trial(gt, min_c, top_k)

        for r1_id, r1_d, r2_id, r2_d, c in ground_truth_list:
            raw_object = {'id': r1_id, 'data': r1_d}
            r1 = TestRecord(raw_object)
            raw_object = {'id': r2_id, 'data': r2_d}
            r2 = TestRecord(raw_object)

            func_info = similarity_function + '("' + r1_d + '","' + r2_d + '")'
            c = eval(func_info)
            p = (c >= min_confidence)
            trial.add_result(r1, r2, p, c)

        eva = Evaluation()
        eva.add_trial(trial)

        assert eva.true_positives() == tp
        assert eva.true_negatives() == tn
        assert eva.false_positives() == fp
        assert eva.false_negatives() == fn
