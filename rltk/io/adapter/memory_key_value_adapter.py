from rltk.io.adapter import KeyValueAdapter


class MemoryKeyValueAdapter(KeyValueAdapter):
    """
    Basic in-memory (dict) adapter.
    """
    def __init__(self):
        self._dict = dict()

    def get(self, key):
        return self._dict.get(key)

    def set(self, key, value: object):
        self._dict[key] = value

    def __next__(self):
        for key, value in self._dict.items():
            yield key, value

    def delete(self, key):
        del self._dict[key]

    def clean(self):
        self._dict = dict()
