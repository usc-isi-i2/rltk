import os
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
        return v[0] if len(v) > 0 else ''


ds1 = rltk.Dataset(reader=rltk.CSVReader(filename='ds1.csv'), record_class=Record1, adapter=rltk.MemoryAdapter())
ds1.build_index()
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader(filename='ds2.jl'), record_class=Record2, adapter=rltk.MemoryAdapter())
ds2.build_index()

# for r in ds1:
#     print(r.id)
# for r in ds2:
#     print(r.id)
# print(ds1.get_record('1').id)


# blocking_file = '/path/to/blocks'
# if not os.path.exists(blocking_file):
#     # rltk.n_gram_blocking(
#     #     iterator1=venture_it,
#     #     tokens1=VentureRecord.assignee_token,
#     #
#     #     iterator2=patent_it,
#     #     field2=PatentRecord.patent_name,
#     #     n_size2=3,
#     #
#     #     output_filename='/path/to/blocks')
#     rltk.inverted_index_blocking(
#         iterator1=venture_it,
#         # tokens1=VentureRecord.assignee_token,
#         attribute1 = VentureRecord.assignee,
#         iterator2=patent_it,
#         tokens2=PatentRecord.patent_token,
#
#         output_filename='/path/to/blocks')
#
feature_vector = []
pairs = rltk.get_record_pairs(ds1, ds2)  # same to without blocks
# pairs = rltk.iterate_on_datasets(ds1, ds2, '/path/to/blocks', batch_size=1000000)
for r1, r2 in pairs:
    print(r1.id, r2.id)
    # v1 = rltk.levenshtein_similarity(r1.value.lower(), r2.value.lower())
    # print(v1)

