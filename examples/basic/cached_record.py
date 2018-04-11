import rltk


@rltk.remove_raw_object
class Record1(rltk.Record):

    @rltk.cached_property
    def id(self):
        print('--> compute id:', self.raw_object['doc_id'])
        return self.raw_object['doc_id']

    @rltk.cached_property
    def value(self):
        print('--> compute value:', self.raw_object['doc_value'])
        return self.raw_object['doc_value']

    @property
    def id_and_value(self):
        print('--> compute id_and_value')
        return self.id + '-' + self.value


arr = [
    {'doc_id': '1', 'doc_value': 'a'},
    {'doc_id': '2', 'doc_value': 'b'},
    {'doc_id': '3', 'doc_value': 'c'}
]
ds1 = rltk.Dataset(reader=rltk.ArrayReader(arr), record_class=Record1)
for r1 in ds1:
    print('------------')
    print('id:', r1.id)
    print('value:', r1.value)
    print('id_and_value:', r1.id_and_value)
    print('cache in dict:', r1.__dict__)
