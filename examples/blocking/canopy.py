import rltk
import math


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

# for r in ds1:
#     print(r.first_name)
# for r in ds2:
#     print(r.first_name)


def vectorize(r):
    return [ord(r.first_name[0].lower()) - 0x61, 2]


def distance_metric(vec1, vec2):
    vec1, vec2 = float(vec1[0]), float(vec2[0])
    return math.sqrt((vec1 - vec2) ** 2)

bg = rltk.CanopyBlockGenerator(t1=10, t2=5, distance_metric=distance_metric)
ks_adapter = bg.generate(
    bg.block(ds1, function_=vectorize),
    bg.block(ds2, function_=vectorize))
pairs = rltk.get_record_pairs(ds1, ds2, block_reader=rltk.BlockReader(ks_adapter))
for r1, r2 in pairs:
    print(r1.id, r1.full_name, '\t', r2.id, r2.full_name)
