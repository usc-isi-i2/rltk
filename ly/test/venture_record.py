import rltk

class VentureRecord(rltk.Record):
    @property
    def id(self):
        return self.r['id']

    @property
    def assignee(self):
        return self.r['assignee']