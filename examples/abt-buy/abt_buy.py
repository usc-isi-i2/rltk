import rltk
tokenizer = rltk.CrfTokenizer()


class AbtRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.brand = ''

    @rltk.cached_property
    def id(self):
        return self.raw_object['id']

    @rltk.cached_property
    def name(self):
        return self.raw_object['name']

    @rltk.cached_property
    def name_tokenized(self):
        tokens = tokenizer.tokenize(self.raw_object['name'])
        for t in tokens:
            t = t.lower()
            if t in brands_list:
                self.brand = t

    @rltk.cached_property
    def description(self):
        return self.raw_object['description']

    @rltk.cached_property
    def price(self):
        return self.raw_object['price']


# class BuyRecord(rltk.Record):
#     @rltk.cached_property
#     def id(self):
#         return self.raw_object['id']
#
#     @rltk.cached_property
#     def name(self):
#         return self.raw_object.get('name')
#
#     @rltk.cached_property
#     def description(self):
#         return self.raw_object.get('description')
#
#     @rltk.cached_property
#     def manufacturer(self):
#         return self.raw_object.get('manufacturer')
#
#     @rltk.cached_property
#     def price(self):
#         return self.raw_object['price']

# load brand list
brands_list = set([])
with open('abt_brands.txt') as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        brands_list.add(line.lower())

ds1 = rltk.Dataset(reader=rltk.CSVReader(open('../../datasets/Abt-Buy/Abt.csv', encoding='latin-1')),
                   record_class=AbtRecord, adapter=rltk.MemoryAdapter())

for r in ds1:
    print(r.id, r.name, 'brand:', r.brand)

# ds2 = rltk.Dataset(reader=rltk.JsonLinesReader('../datasets/Abt-Buy/Buy.csv'),
#                    record_class=BuyRecord, adapter=rltk.MemoryAdapter())

# pairs = rltk.get_record_pairs(ds1, ds2)
# for r1, r2 in pairs:
#     print('-------------')
#     print(r1.id, r1.value, '\t', r2.id, r2.value)
#     print('levenshtein_distance:', rltk.levenshtein_distance(r1.value, r2.value))
#     print('levenshtein_similarity:', rltk.levenshtein_similarity(r1.value, r2.value))
