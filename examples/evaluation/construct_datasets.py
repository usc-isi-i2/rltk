import rltk


@rltk.remove_raw_object
class EvaluationRecord(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data(self):
        return self.raw_object['data']


@rltk.remove_raw_object
class EvaluationRecord2(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def data2(self):
        return self.raw_object['data2']


dataset_1_file_name = 'data_1.csv'
dataset_2_file_name = 'data_2.csv'

ds1 = rltk.Dataset(reader=rltk.CSVReader(dataset_1_file_name),
                   record_class=EvaluationRecord)
ds2 = rltk.Dataset(reader=rltk.CSVReader(dataset_2_file_name),
                   record_class=EvaluationRecord2)
