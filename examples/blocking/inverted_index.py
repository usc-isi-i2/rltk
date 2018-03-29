import rltk


class Record1(rltk.Record):
    remove_raw_object = True

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


class Record2(rltk.Record):
    remove_raw_object = True

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
def tokenizer(r):
    return ngram.basic(r.first_name, 3)

block_handler = rltk.InvertedIndexBlockGenerator(
    ds1, ds2, writer=rltk.BlockFileWriter('ngram_blocks.jl'), tokenizer=tokenizer).generate()
pairs = rltk.get_record_pairs(ds1, ds2, rltk.BlockFileReader(block_handler))
for r1, r2 in pairs:
    print(r1.id, r1.full_name, '\t', r2.id, r2.full_name)
