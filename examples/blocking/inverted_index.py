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

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name


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

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

ds1 = rltk.Dataset(reader=rltk.CSVReader('ds1.csv', delimiter=','), record_class=Record1)
ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('ds2.jl'), record_class=Record2)

ngram = rltk.NGramTokenizer()

bg = rltk.TokenBlockGenerator()
block1 = bg.block(ds1, function_=lambda r: ngram.basic(r.first_name, 3),
                  block=rltk.Block(rltk.LevelDbKeySetAdapter('block_store', 'b1', clean=True)))
block2 = bg.block(ds2, function_=lambda r: ngram.basic(r.first_name, 3),
                  block=rltk.Block(rltk.LevelDbKeySetAdapter('block_store', 'b2', clean=True)))
block3 = bg.generate(block1, block2, rltk.Block(rltk.LevelDbKeySetAdapter('block_store', 'b3', clean=True)))
pairs = rltk.get_record_pairs(ds1, ds2, block=block3)
for r1, r2 in pairs:
    print(r1.id, r1.full_name, '\t', r2.id, r2.full_name)
