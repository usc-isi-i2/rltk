import pytest

from ..tokenizer import q_grams
from ..levenshtein import Levenshtein, NormalizedLevenshtein

def test_q_grams():
    assert q_grams('abc', 3) == ['##a', '#ab', 'abc', 'bc#', 'c##']

@pytest.mark.parametrize('s1, s2, distance, similarity', [
    ('abc', 'def', 3, 0.0),
    ('aaa', 'aaa', 0, 1.0),
    (None, 'abc', None, None),
    ('abc', None, None, None)
])
def test_levenshtein(s1, s2, distance, similarity):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError) as ex:
            Levenshtein(s1, s2)
    else:
        lev = Levenshtein(s1, s2)
        assert lev.distance() == distance
        assert lev.similarity() == similarity
