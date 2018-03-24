import rltk


class Record1(rltk.Record):
    @property
    def id(self):
        return self.raw_object['doc_id']

    @property
    def value(self):
        return self.raw_object['doc_value']


class Record2(rltk.Record):
    @property
    def id(self):
        return self.raw_object['ident']

    @property
    def value(self):
        v = self.raw_object.get('values', list())
        return v[0] if len(v) > 0 else 'empty'


ds1 = rltk.Dataset(reader=rltk.CSVReader('ds1.csv'),
                   record_class=Record1, adapter=rltk.MemoryAdapter())
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'),
                   record_class=Record2, adapter=rltk.DBMAdapter('file_index'))

pairs = rltk.get_record_pairs(ds1, ds2)
for r1, r2 in pairs:
    print('-------------')
    print(r1.id, r1.value, '\t', r2.id, r2.value)
    print('levenshtein_distance:', rltk.levenshtein_distance(r1.value, r2.value))
    print('levenshtein_similarity:', rltk.levenshtein_similarity(r1.value, r2.value))
