from abc import ABC, abstractmethod
from typing import List
from rltk.tokenizer.crf_tokenizer import crf_tokenizer as dig_tokenizer


class Tokenizer(ABC):
    """
    Abstract tokenizer
    """

    @abstractmethod
    def tokenize(self, s: str) -> List[str]:
        """
        Apply tokenizer

        Args:
            s (str): String to tokenize.

        Returns:
            List[str]: Tokenized list. It won't do token deduplication.
        """
        raise NotImplementedError


class CRFTokenizer(Tokenizer):
    """
    CRFTokenizer: this uses old DIG CRFTokenizer
    """

    def __init__(self, *args, **kwargs) -> None:
        self._t = dig_tokenizer.CrfTokenizer(*args, **kwargs)

    def tokenize(self, s: str) -> List[str]:
        return self._t.tokenize(s)


class WordTokenizer(Tokenizer):
    """
    Word Tokenizer: tokenize word by white space

    Args:
        remove_empty (bool, optional): If set, empty token will be removed. Defaults to False.
    """

    def __init__(self, remove_empty: bool = False) -> None:
        self._remove_empty = remove_empty

    def tokenize(self, s: str) -> List[str]:
        s = s.split(' ')
        if self._remove_empty:
            return list(filter(lambda x: len(x) != 0, s))
        else:
            return s


class NGramTokenizer(Tokenizer):
    """
    NGrame Tokenizer

    Args:
         n (int): n.
         place_holder (str, optional): String to fill pad and separator. Defaults to white space (' ').
         padded (bool, optional): If set, head the tail will be filled with pad. Defaults to False.
    """

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
