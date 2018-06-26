import rltk


tokenizer = rltk.CrfTokenizer()


def extract_possible_model(s):
    tokens = s.split(' ')

    has_digit = has_alpha = False
    for t in tokens:
        if len(t) < 5:
            continue
        for c in t:
            if c.isdigit():
                has_digit = True
            elif c.isalpha():
                has_alpha = True
            if has_digit and has_alpha:
                return t
    return ''


def tokenize(s):
    tokens = tokenizer.tokenize(s)
    return [w.lower() for w in tokens if w.isalpha()]


def get_brand_name(tokens):
    for word_len in range(min(5, len(tokens)), 0, -1):
        i = 0; j = i + word_len
        while j <= len(tokens):
            name = ' '.join(tokens[i:j])
            if name in brand_list:
                return name
            i += 1; j += 1
    return ''

# brand_map = {
#     't1': (b1, b2, b3)
# }
# brand_map = {}
brand_list = set([])
with open('abt_brands.txt') as f:
    for line in f:
        line = line.strip().lower()
        if len(line) == 0:
            continue
        brand_list.add(' '.join(tokenize(line)))
        # tokens = tokenize(line)
        # for t in tokens:
        #     brand_map[t] = brand_map.get(t, set([]))
        #     brand_map[t].add(line)
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
    def name_tokens(self):
        tokens = tokenize(self.raw_object['name'])

        self.brand = get_brand_name(tokens)
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

        return set(tokens)

    @rltk.cached_property
    def model(self):
        ss = self.raw_object['name'].split(' - ')
        return ss[-1].strip() if len(ss) > 1 else ''

    @rltk.cached_property
    def description(self):
        return self.raw_object.get('description', '')

    @rltk.cached_property
    def price(self):
        p = self.raw_object.get('price', '')
        if p.startswith('$'):
            p = p[1:]
        return p

    @rltk.cached_property
    def brand_cleaned(self):
        _ = self.name_tokens
        return self.brand

    @rltk.cached_property
    def model_cleaned(self):
        m = self.model
        return m.lower().replace('-', '').replace('/', '').replace('&', '')


class BuyRecord(rltk.Record):
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
    def name_tokens(self):
        tokens = tokenize(self.raw_object['name'])
        self.brand = get_brand_name(tokens)
        return set(tokens)

    @rltk.cached_property
    def description(self):
        return self.raw_object.get('description', '')

    @rltk.cached_property
    def manufacturer(self):
        return self.raw_object.get('manufacturer', '').lower()

    @rltk.cached_property
    def price(self):
        p = self.raw_object.get('price', '')
        if p.startswith('$'):
            p = p[1:]
        return p

    @rltk.cached_property
    def model(self):
        ss = self.raw_object['name'].split(' - ')
        if len(ss) > 1:
            return ss[-1].strip()
        else:
            return extract_possible_model(self.raw_object['name'])

    @rltk.cached_property
    def brand_cleaned(self):
        _ = self.name_tokens
        manufacturer = self.manufacturer
        return manufacturer if manufacturer != '' else self.brand

    @rltk.cached_property
    def model_cleaned(self):
        m = self.model
        return m.lower().replace('-', '').replace('/', '').replace('&', '')


ds_abt = rltk.Dataset(reader=rltk.CSVReader(open('../../datasets/Abt-Buy/Abt.csv', encoding='latin-1')),
                   record_class=AbtRecord, adapter=rltk.MemoryAdapter())

ds_buy = rltk.Dataset(reader=rltk.CSVReader(open('../../datasets/Abt-Buy/Buy.csv', encoding='latin-1')),
                   record_class=BuyRecord, adapter=rltk.MemoryAdapter())

# statistics
print_details = False
name_count = model_count = description_count = price_count = brand_count = 0
for r in ds_abt:
    name_count += 1
    print('------\nname:', r.name) if print_details else ''
    if len(r.description) > 0:
        description_count += 1
    if len(r.price) > 0:
        price_count += 1
    if len(r.model) > 0:
        model_count += 1
        print('model:', r.model)  if print_details else ''
    if len(r.brand) > 0:
        brand_count += 1
        print('brand:', r.brand)  if print_details else ''
    else:
        print('no brand') if print_details else ''
name_count = float(name_count)
print('description:', description_count / name_count,
      'price:', price_count / name_count,
      'brand', brand_count / name_count,
      'model', model_count / name_count)

# cat abt_buy_perfectMapping.csv |  awk '{split($0,a,"," ); print a[2]}' | sort | uniq -c | grep "2 "


name_count = description_count = price_count = brand_count = model_count = manufacturer_count = 0
for r in ds_buy:
    name_count += 1
    print('------\nname:', r.name) if print_details else ''
    if len(r.description) > 0:
        description_count += 1
    if len(r.price) > 0:
        price_count += 1
    if len(r.model) > 0:
        model_count += 1
        print('model:', r.model) if print_details else ''
    if len(r.brand) > 0:
        brand_count += 1
        print('brand:', r.brand) if print_details else ''
    else:
        print('no brand') if print_details else ''
    if len(r.manufacturer) > 0:
        manufacturer_count += 1
        # print('manufacturer:', r.manufacturer)
    # else:
    #     print('no manufacturer:', r.name)

name_count = float(name_count)
print('description:', description_count / name_count,
      'price:', price_count / name_count,
      'brand', brand_count / name_count,
      'model', model_count / name_count,
      'manufacturer', manufacturer_count / name_count)


