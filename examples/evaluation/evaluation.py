import rltk
from rltk.evaluation.evaluation import Evaluation
from rltk.evaluation.ground_truth import GroundTruth
from rltk.evaluation.trial import Trial
from rltk.similarity import *


class EvaluationRecord(rltk.Record):
    remove_raw_object = True

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data(self):
        return self.raw_object['data']


gt = GroundTruth()

ground_truth_list = [('0', '', '10', 'abc', False), ('1', 'abc', '11', 'abc', True), ('2', 'abcd', '12', 'abc', False),
                     ('3', 'abd', '13', 'abc', False)]

for r1_id, r1_d, r2_id, r2_d, p in ground_truth_list:
    raw_object = {'id': r1_id, 'data': r1_d}
    r1 = EvaluationRecord(raw_object)
    raw_object = {'id': r2_id, 'data': r2_d}
    r2 = EvaluationRecord(raw_object)
    gt.add_ground_truth(r1, r2, p)

file_name = 'ground_truth.csv'

gt.save(file_name)

gt1 = GroundTruth()
gt1.load(file_name)

similarity_info = [('0', '', '10', 'abc'), ('1', 'abc', '11', 'abc'), ('2', 'abcd', '12', 'abc'),
                   ('3', 'abd', '13', 'abc')]

min_c = 0
top_k = 0
min_confidence = 0.5
similarity_function = 'levenshtein_similarity'

trial = Trial(gt, min_c, top_k)

for r1_id, r1_d, r2_id, r2_d in similarity_info:
    raw_object = {'id': r1_id, 'data': r1_d}
    r1 = EvaluationRecord(raw_object)
    raw_object = {'id': r2_id, 'data': r2_d}
    r2 = EvaluationRecord(raw_object)

    func_info = similarity_function + '("' + r1_d + '","' + r2_d + '")'
    c = eval(func_info)
    p = (c >= min_confidence)
    trial.add_result(r1, r2, p, c)

eva = Evaluation()
eva.add_trial(trial)

print('true positive is: ' + str(eva.true_positives()))
