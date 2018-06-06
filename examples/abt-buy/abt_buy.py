import rltk


tokenizer = rltk.CrfTokenizer()


def tokenize(s):
    tokens = tokenizer.tokenize(s)
    return [w.lower() for w in tokens if w.isalpha()]

# brand_map = {
#     't1': (b1, b2, b3)
# }
brand_map = {}
brand_list = set([])
with open('abt_brands.txt') as f:
    for line in f:
        line = line.strip().lower()
        if len(line) == 0:
            continue
        brand_list.add(' '.join(tokenize(line)))
        tokens = tokenize(line)
        for t in tokens:
            brand_map[t] = brand_map.get(t, set([]))
            brand_map[t].add(line)
# print(brand_list)


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
        tokens = tokenize(self.raw_object['name'])

        for word_len in range(min(5, len(tokens)), 0, -1):
            i = 0; j = i + word_len
            while j <= len(tokens):
                name = ' '.join(tokens[i:j])
                if name in brand_list:
                    self.brand = name
                    break
                i += 1; j += 1

        # candidate_brands = {}
        # for t in tokens:
        #     t = t.lower()
        #     if t in brand_map:
        #         for b in brand_map[t]:
        #             candidate_brands[b] = candidate_brands.get(b, 0)
        #             candidate_brands[b] += 1
        #
        # if len(candidate_brands) > 0:
        #     self.brand = max(candidate_brands.keys(), key=(lambda key: candidate_brands[key]))
            # self.brand =

        return tokens

    @rltk.cached_property
    def model(self):
        ss = self.raw_object['name'].split('-')
        return ss[-1].strip() if len(ss) > 0 else ''

    @rltk.cached_property
    def description(self):
        return self.raw_object.get('description', '')

    @rltk.cached_property
    def price(self):
        return self.raw_object.get('price', '')


# class BuyRecord(rltk.Record):
#     def __init__(self, raw_object):
#         super().__init__(raw_object)
#         self.brand = ''
#
#     @rltk.cached_property
#     def id(self):
#         return self.raw_object['id']
#
#     @rltk.cached_property
#     def name(self):
#         return self.raw_object['name']
#
#     @rltk.cached_property
#     def name_tokenized(self):
#         tokens = tokenizer.tokenize(self.raw_object['name'])
#         for t in tokens:
#             t = t.lower()
#             if t in brands_list:
#                 self.brand = t
#
#     @rltk.cached_property
#     def description(self):
#         return self.raw_object.get('description', '')
#
#     @rltk.cached_property
#     def manufacturer(self):
#         return self.raw_object.get('manufacturer', '').lower()
#
#     @rltk.cached_property
#     def price(self):
#         return self.raw_object.get('price', '')



ds_abt = rltk.Dataset(reader=rltk.CSVReader(open('../../datasets/Abt-Buy/Abt.csv', encoding='latin-1')),
                   record_class=AbtRecord, adapter=rltk.MemoryAdapter())

# ds_buy = rltk.Dataset(reader=rltk.CSVReader(open('../../datasets/Abt-Buy/Buy.csv', encoding='latin-1')),
#                    record_class=BuyRecord, adapter=rltk.MemoryAdapter())

# statistics
name_count = model_count = description_count = price_count = brand_count = 0
for r in ds_abt:
    name_count += 1
    # print('------\nname', r.name)
    if len(r.description) > 0:
        description_count += 1
    if len(r.price) > 0:
        price_count += 1
    if len(r.model) > 0:
        model_count += 1
        # print('model', r.model)
    if len(r.brand) > 0:
        brand_count += 1
        # print('brand:', r.brand)
    else:
        print('------\nname', r.name)
        print('no brand')
name_count = float(name_count)
print('description:', description_count / name_count,
      'price:', price_count / name_count,
      'brand', brand_count / name_count,
      'model', model_count / name_count)




# name_count = description_count = price_count = brand_count = manufacturer_count = 0
# for r in ds_buy:
#     name_count += 1
#     if len(r.description) > 0:
#         description_count += 1
#     if len(r.price) > 0:
#         price_count += 1
#     if len(r.brand) > 0:
#         brand_count += 1
#     else:
#         print('no brand:', r.name)
#     if len(r.manufacturer) > 0:
#         manufacturer_count += 1
# name_count = float(name_count)
# print(description_count / name_count, price_count / name_count,
#       brand_count / name_count, manufacturer_count / name_count)


# pairs = rltk.get_record_pairs(ds1, ds2)
# for r1, r2 in pairs:
#     print('-------------')
#     print(r1.id, r1.value, '\t', r2.id, r2.value)
#     print('levenshtein_distance:', rltk.levenshtein_distance(r1.value, r2.value))
#     print('levenshtein_similarity:', rltk.levenshtein_similarity(r1.value, r2.value))
