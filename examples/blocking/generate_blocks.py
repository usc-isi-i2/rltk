import rltk


@rltk.remove_raw_object
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


@rltk.remove_raw_object
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


ds1 = rltk.Dataset(reader=rltk.CSVReader('ds1.csv', delimiter=','),
                   record_class=Record1, adapter=rltk.MemoryDatasetAdapter())
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'),
                   record_class=Record2, adapter=rltk.MemoryDatasetAdapter())

print('--- block on first_name ---')
bg = rltk.HashBlockGenerator()
block_writer = rltk.BlockWriter()
bg.generate(bg.block(ds1, property_='first_name'),
            bg.block(ds2, property_='first_name'),
            block_writer)

block_reader = rltk.BlockReader(block_writer.key_set_adapter)
pairs = rltk.get_record_pairs(ds1, ds2, block_reader)
for r1, r2 in pairs:
    print(r1.id, r1.first_name, '\t', r2.id, r2.first_name)


print('--- block on first_name[:1] ---')
bg2 = rltk.HashBlockGenerator()
ks_adapter2 = bg2.generate(
            bg2.block(ds1, function_=lambda r: r.first_name[:1]),
            bg2.block(ds2, function_=lambda r: r.first_name[:1]))

pairs = rltk.get_record_pairs(ds1, ds2, rltk.BlockReader(ks_adapter2))
for r1, r2 in pairs:
    print(r1.id, r1.first_name, '\t', r2.id, r2.first_name)
