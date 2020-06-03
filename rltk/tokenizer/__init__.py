from abc import ABC, abstractmethod
from typing import List
from rltk.tokenizer.crf_tokenizer import crf_tokenizer as dig_tokenizer


class Tokenizer(ABC):

    @abstractmethod
    def tokenize(self, s):
        raise NotImplementedError


class CRFTokenizer(Tokenizer):

    def __init__(self, *args, **kwargs):
        self._t = dig_tokenizer.CrfTokenizer(*args, **kwargs)

    def tokenize(self, s):
        return self._t.tokenize(s)


class WordTokenizer(Tokenizer):
    def __init__(self, remove_empty: bool = False):
        self._remove_empty = remove_empty

    def tokenize(self, s):
        s = s.split(' ')
        if self._remove_empty:
            return list(filter(lambda x: len(x) != 0, s))
        else:
            return s


class NGramTokenizer(Tokenizer):

    def __init__(self, n: int, place_holder: str = ' ', padded: bool = False,
                 base_tokenizer: Tokenizer = None) -> None:
        self._n = n
        self._place_holder = place_holder
        self._padded = padded
        self._base_tokenizer = base_tokenizer if base_tokenizer else WordTokenizer()

    def tokenize(self, s: str) -> List[str]:
        if len(s) == 0:
            return []
        if self._padded:
            pad = self._place_holder * (self._n - 1)
            s = pad + s + pad
        s = self._base_tokenizer.tokenize(s)
        s = self._place_holder.join(s)
        if len(s) < self._n:
            return [s]
        return [s[i:i + self._n] for i in range(len(s) - self._n + 1)]
