import rltk
import json


@rltk.remove_raw_object
class EvaluationRecord(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data(self):
        return self.raw_object['data']


@rltk.remove_raw_object
class PatentDataRecord(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['pnum']

    @rltk.cached_property
    def pnum(self):
        return self.raw_object['pnum']

    @rltk.cached_property
    def ayear(self):
        return self.raw_object['ayear']

    @rltk.cached_property
    def firstassignee(self):
        return self.raw_object['firstassignee']

    @rltk.cached_property
    def patassg_group_bfh_2017(self):
        return self.raw_object['patassg_group_bfh_2017']

    @rltk.cached_property
    def appdate(self):
        return self.raw_object['appdate']

    @rltk.cached_property
    def source_bfh_2017(self):
        return self.raw_object['source_bfh_2017']

    @rltk.cached_property
    def patassg_group_bfh_2014(self):
        return self.raw_object['patassg_group_bfh_2014']

    @rltk.cached_property
    def bfhcode(self):
        return self.raw_object['bfhcode']


@rltk.remove_raw_object
class CentureRecord(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.VXFirm_ID

    @rltk.cached_property
    def VXFirm_ID(self):
        return self.raw_object['\ufeffVXFirm_ID']

    @rltk.cached_property
    def Company_Name(self):
        return self.raw_object['Company_Name']


gt = rltk.GroundTruth()

saved_ground_truth_file_name = 'label.jsonl'

# f = open(saved_ground_truth_file_name, 'r')
# for line in f.readlines():
#     line = json.loads(line.strip())
#     if not len(line):
#         continue
#     gt.add_ground_truth(line['id'][0], line['id'][1], line['label'])
#
# gt.save('saved_' + saved_ground_truth_file_name)
gt.load('saved_' + saved_ground_truth_file_name)

dataset_1_file_name = 'PatentData4_Sunil_V1_sample.txt'
dataset_2_file_name = 'VentureExpertData_sample.csv'

dataset_1_adapter_name = 'PatentData4_Sunil_V1_sample_ada'
dataset_2_adapter_name = 'VentureExpertData_sample_ada'

ds1 = rltk.Dataset(reader=rltk.CSVReader(dataset_1_file_name, delimiter='\t'),
                   record_class=PatentDataRecord, adapter=rltk.DBMAdapter(dataset_1_adapter_name))

ds2 = rltk.Dataset(reader=rltk.CSVReader(dataset_2_file_name, delimiter=','),
                   record_class=CentureRecord, adapter=rltk.DBMAdapter(dataset_2_adapter_name))


trial = rltk.Trial(gt, min_confidence=0.5, top_k=0)
min_confidence = 0.5
pairs = rltk.get_record_pairs(ds1, ds2)
for r1, r2 in pairs:
    c = rltk.levenshtein_similarity(r1.firstassignee, r2.Company_Name)
    p = (c >= min_confidence)
    trial.add_result(r1, r2, p, c)

eva = rltk.Evaluation()
eva.add_trial(trial)

print('precision is: ' + str(eva.precision()))
print('true positive is: ' + str(eva.true_positives()))
print('false negative is: ' + str(eva.false_negatives()))
