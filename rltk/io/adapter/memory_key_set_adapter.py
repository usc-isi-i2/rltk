from rltk.io.adapter.key_set_adapter import KeySetAdapter


class MemoryKeySetAdapter(KeySetAdapter):

    def __init__(self):
        self._store = dict()

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        if not isinstance(value, set):
            raise ValueError('value must be a set')
        self._store[key] = value

    def add(self, key, value):
        if key not in self._store:
            self._store[key] = set()
        self._store[key].add(value)

    def remove(self, key, value):
        self._store[key].remove(value)

    def delete(self, key):
        del self._store[key]

    def clean(self):
        self._store = dict()

    def __next__(self):
        for k, v in self._store.items():
            yield k, v
