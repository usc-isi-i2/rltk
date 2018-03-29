import rltk


class Record1(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['doc_id']

    @rltk.cached_property
    def first_name(self):
        return self.raw_object['first name']

    @rltk.cached_property
    def last_name(self):
        return self.raw_object['last name']


class Record2(rltk.Record):
    @rltk.cached_property
    def id(self):
        return self.raw_object['ident']

    @rltk.cached_property
    def first_name(self):
        return self.raw_object['name'].split(' ')[0]

    @rltk.cached_property
    def last_name(self):
        return self.raw_object['name'].split(' ')[1]


def blocking_function(r1, r2):
    return r1.first_name[:1] == r2.first_name[:1]


ds1 = rltk.Dataset(reader=rltk.CSVReader('ds1.csv', delimiter=','), record_class=Record1)
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'), record_class=Record2)

block_handler = rltk.CustomBlockGenerator(
    ds1, ds2, custom_function=blocking_function,
    writer=rltk.BlockArrayWriter()).generate()
pairs = rltk.get_record_pairs(ds1, ds2, rltk.BlockArrayReader(block_handler))
for r1, r2 in pairs:
    print(r1.id, r1.first_name, '\t', r2.id, r2.first_name)
