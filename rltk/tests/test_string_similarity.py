import pytest

from ..string_similarity.tokenizer import q_grams
from ..string_similarity import *

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
            levenshtein_similarity(s1, s2)
        with pytest.raises(ValueError) as ex:
            levenshtein_distance(s1, s2)
    else:
        assert levenshtein_distance(s1, s2) == distance
        assert levenshtein_similarity(s1, s2) == similarity

@pytest.mark.parametrize('s, code', [
    ('Soundex',    'S532'), ('Example',     'E251'),
    ('Sownteks',   'S532'), ('Ekzampul',    'E251'),
    ('Euler',      'E460'), ('Gauss',       'G200'),
    ('Hilbert',    'H416'), ('Knuth',       'K530'),
    ('Lloyd',      'L300'), ('Lukasiewicz', 'L222'),
    ('Ellery',     'E460'), ('Ghosh',       'G200'),
    ('Heilbronn',  'H416'), ('Kant',        'K530'),
    ('Ladd',       'L300'), ('Lissajous',   'L222'),
    ('Wheaton',    'W350'), ('Burroughs',   'B620'),
    ('Burrows',    'B620'), ('O\'Hara',     'O600'),
    ('Washington', 'W252'), ('Lee',         'L000'),
    ('Gutierrez',  'G362'), ('Pfister',     'P236'),
    ('Jackson',    'J250'), ('Tymczak',     'T522'),
    ('VanDeusen',  'V532'), ('Ashcraft',    'A261'),
    ('Gutierrez',  'G362'),
])
def test_soundex(s, code):
    if s is None:
        with pytest.raises(ValueError) as ex:
            soundex(s)
    if isinstance(s, int):
        with pytest.raises(TypeError) as ex:
            soundex(s)
    else:
        assert soundex(s) == code