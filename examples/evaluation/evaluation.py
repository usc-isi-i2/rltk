import rltk


class EvaluationRecord(rltk.Record):
    remove_raw_object = True

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data(self):
        return self.raw_object['data']


class GroundTruthRecord(rltk.Record):
    remove_raw_object = True

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def id1(self):
        return self.raw_object['id1']

    @rltk.cached_property
    def id2(self):
        return self.raw_object['id2']

    @rltk.cached_property
    def data1(self):
        return self.raw_object['data1']

    @rltk.cached_property
    def data2(self):
        return self.raw_object['data2']

    @rltk.cached_property
    def label(self):
        return self.raw_object['label']


gt = rltk.GroundTruth()

grond_truth_file_name = 'ground_truth.csv'

ds1 = rltk.Dataset(reader=rltk.CSVReader(grond_truth_file_name),
                   record_class=GroundTruthRecord)

for record in ds1:
    raw_object = {'id': record.id1, 'data': record.data1}
    r1 = EvaluationRecord(raw_object)
    raw_object = {'id': record.id2, 'data': record.data2}
    r2 = EvaluationRecord(raw_object)
    gt.add_ground_truth(r1, r2, record.label)

saved_ground_truth_file_name = 'saved_ground_truth.csv'

gt.save(saved_ground_truth_file_name)

gt1 = rltk.GroundTruth()
gt1.load(saved_ground_truth_file_name)

min_confidence = 0.5
similarity_function = 'levenshtein_similarity'

trial = rltk.Trial(gt, min_confidence=0.5, top_k=0)

for record in ds1:
    raw_object = {'id': record.id1, 'data': record.data1}
    r1 = EvaluationRecord(raw_object)
    raw_object = {'id': record.id2, 'data': record.data2}
    r2 = EvaluationRecord(raw_object)

    func_info = "rltk." + similarity_function + '("' + record.data1 + '","' + record.data2 + '")'
    c = eval(func_info)
    p = (c >= min_confidence)
    trial.add_result(r1, r2, p, c)

eva = rltk.Evaluation()
eva.add_trial(trial)

print('true positive is: ' + str(eva.true_positives()))
