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
                   record_class=Record1, adapter=rltk.MemoryAdapter())
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'),
                   record_class=Record2, adapter=rltk.MemoryAdapter())

# for r in ds1:
#     print(r.id, r.first_name, r.last_name)
# for r in ds2:
#     print(r.id, r.first_name, r.last_name)

block_writer = rltk.BlockFileWriter('blocks.jl')
# block_writer = rltk.BlockArrayWriter()
block_writer.write('1', 'a')
block_writer.write('2', 'b')
block_writer.write('2', 'd')
block_writer.write('1', 'a')
block_writer.flush() # flush / close must be called in order to read later

block_reader = rltk.BlockFileReader('blocks.jl')
# block_reader = rltk.BlockArrayReader(block_writer.get_handler())
pairs = rltk.get_record_pairs(ds1, ds2, block_reader)
for r1, r2 in pairs:
    print(r1.id, r1.first_name, '\t', r2.id, r2.first_name)
