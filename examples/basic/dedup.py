import rltk


raw_inputs = [
    {'name': 'a1', 'age': 10, 'id': 1},
    {'name': 'a2', 'age': 20, 'id': 2},
    {'name': 'a3', 'age': 30, 'id': 3},
    {'name': 'a3', 'age': 30, 'id': 4},
    {'name': 'a1', 'age': 10, 'id': 5},
]


class MyRecord(rltk.Record):

    @property
    def id(self):
        return str(self.raw_object['id'])

    @property
    def name(self):
        return self.raw_object['name']

    @property
    def age(self):
        return self.raw_object['age']


ds = rltk.Dataset(reader=rltk.ArrayReader(raw_inputs), record_class=MyRecord)
for r, r_ in rltk.get_record_pairs(ds):
    print('comparing', r.id, r_.id, r.name == r_.name and r.age == r_.age)
