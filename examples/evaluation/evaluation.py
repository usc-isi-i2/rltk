import rltk


class EvaluationRecord(rltk.Record):
    remove_raw_object = True

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data(self):
        return self.raw_object['data']

class EvaluationRecord2(rltk.Record):
    remove_raw_object = True

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data2(self):
        return self.raw_object['data2']

saved_ground_truth_file_name = 'ground_truth.csv'
gt = rltk.GroundTruth()
gt.load(saved_ground_truth_file_name)

gt.add_ground_truth('1', '12', True)
gt.save('saved_' + saved_ground_truth_file_name)

dataset_1_file_name = 'data_1.csv'
dataset_2_file_name = 'data_2.csv'

ds1 = rltk.Dataset(reader=rltk.CSVReader(dataset_1_file_name),
                   record_class=EvaluationRecord)
ds2 = rltk.Dataset(reader=rltk.CSVReader(dataset_2_file_name),
                   record_class=EvaluationRecord2)

trial = rltk.Trial(gt, min_confidence=0.5, top_k=0, save_record=True, key_1='data', key_2='data2')
min_confidence = 0.5
pairs = rltk.get_record_pairs(ds1, ds2)
for r1, r2 in pairs:
    c = rltk.levenshtein_similarity(r1.data, r2.data2)
    p = (c >= min_confidence)
    trial.add_result(r1, r2, p, c)

trial.evaluation()
# eva = rltk.Evaluation()
# eva.add_trial(trial)


print('precision is: ' + str(trial.precision()))
print('true positive is: ' + str(trial.true_positives()))
print('false negative is: ' + str(trial.false_negatives()))
print('false positive is: ' + str(trial.false_positives()))

for result_data in trial.get_all_data():
    print(result_data.full_data)
