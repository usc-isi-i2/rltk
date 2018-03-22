# -*- coding: utf-8 -*-

import pytest

# from ..similarity.tokenizer import q_grams
from rltk.similarity import *

# only test hash code for phonetic algorithms
from rltk.similarity.nysiis import _nysiis
from rltk.similarity.soundex import _soundex
from rltk.similarity.metaphone import _metaphone


@pytest.mark.parametrize('n1, n2, epsilon, equal', [
    (1, 2, 0, 0),
    (-1, -2, 0, 0),
    (3.2, 3.0, 0.15, 0),
    (3.2, 3.0, 0.3, 1)
])
def test_number_equal(n1, n2, epsilon, equal):
    if not isinstance(n1, (int, float)) or not isinstance(n2, (int, float)):
        with pytest.raises(ValueError):
            number_equal(n1, n2)
    else:
        assert number_equal(n1, n2, epsilon) == equal


@pytest.mark.parametrize('s1, s2, equal', [
    ('abc', 'abc', 1),
    ('hello', 'hello', 1),
    (None, 'ok', None),
    (1, 2, None),
    ('bar', 'foo', 0)
])
def test_string_equal(s1, s2, equal):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            string_equal(s1, s2)
    elif not isinstance(s1, str) or not isinstance(s2, str):
        with pytest.raises(TypeError):
            string_equal(s1, s2)
    else:
        assert string_equal(s1, s2) == equal


@pytest.mark.parametrize('s1, s2, distance', [
    ('abc', 'abc', 0),
    ('acc', 'abcd', None),
    ('testing', 'test', None),
    ('hello~', 'alloha', 5),
    ([1, 2, 3], [3, 2, 3], 1),
    ([2, 3, 1], [3, 2, 1], 2)
])
def test_hamming_distance(s1, s2, distance):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            hamming_distance(s1, s2)
    if len(s1) != len(s2):
        with pytest.raises(ValueError):
            hamming_distance(s1, s2)
    else:
        assert hamming_distance(s1, s2) == distance


@pytest.mark.parametrize('set1, set2, similarity', [
    (set(['data', 'science']), set(['data']), 0.667),
    (set([1, 1, 2, 3, 4]), set([2, 3, 4, 5, 6, 7, 7, 8]), 0.545)
])
def test_dice_similarity(set1, set2, similarity):
    if set1 is None or set2 is None:
        with pytest.raises(ValueError):
            dice_similarity(set1, set2)
    else:
        assert pytest.approx(dice_similarity(set1, set2), 0.001) == similarity


@pytest.mark.parametrize('s1, s2, distance, similarity', [
    ('abc', 'def', 3, 0.0),
    ('aaa', 'aaa', 0, 1.0),
    (None, 'abc', None, None),
    ('abc', None, None, None)
])
def test_levenshtein(s1, s2, distance, similarity):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            levenshtein_similarity(s1, s2)
        with pytest.raises(ValueError):
            levenshtein_distance(s1, s2)
    else:
        assert levenshtein_distance(s1, s2) == distance
        assert levenshtein_similarity(s1, s2) == similarity


@pytest.mark.parametrize('s1, s2, insert, delete, substitute,'
                         'insert_default, delete_default, substitute_default, distance', [
                             ('', 'abc', {'c': 50}, {}, {}, 100, 100, 100, 250),
                             ('a', 'abc', {'c': 50}, {}, {}, 100, 100, 100, 150),
                             ('ab', 'abc', {'c': 50}, {}, {}, 100, 100, 100, 50),
                             ('abc', 'abc', {'c': 50}, {}, {}, 100, 100, 100, 0),
                             ('abcd', 'abc', {}, {'d': 50}, {}, 100, 100, 100, 50),
                             ('abd', 'abc', {}, {}, {'d': {'c': 50}}, 100, 100, 100, 50),
                         ])
def test_weighted_levenshtein(s1, s2, insert, delete, substitute,
                              insert_default, delete_default, substitute_default, distance):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            levenshtein_distance(s1, s2, insert, delete, substitute,
                                 insert_default, delete_default, substitute_default)
    else:
        assert levenshtein_distance(s1, s2, insert, delete, substitute,
                                    insert_default, delete_default, substitute_default) == distance


@pytest.mark.parametrize('s1, s2, distance', [
    ('', '', 0),
    ('abc', '', 3),
    ('bc', 'abc', 1),
    ('fuor', 'four', 1),
    ('abcd', 'acb', 2),
    ('cape sand recycling', 'edith ann graham', 16),
    ('jellyifhs', 'jellyfish', 2),
    ('ifhs', 'fish', 2),
    ('Hello, world!', 'Hello,Â world!', 2),
])
def test_damerau_levenshtein(s1, s2, distance):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            damerau_levenshtein_distance(s1, s2)
    else:
        assert damerau_levenshtein_distance(s1, s2) == distance


@pytest.mark.parametrize('s1, s2, score', [
    ('John Singer Sargent', 'John S. Sargent', 25),
    ('John Singer Sargent', 'Jane Klinger Sargent', 28.5),
    ('John Stanislaus Sargent', 'John S. Sargent', 23)
])
def test_needleman_wunsch(s1, s2, score):
    if s1 is None or s2 is None:
        with pytest.raises(ValueError):
            needleman_wunsch_score(s1, s2)
    else:
        assert needleman_wunsch_score(s1, s2) == score


@pytest.mark.parametrize('s1, s2, distance', [
    ('dixon', 'dicksonx', 0.767),
    ('martha', 'marhta', 0.944),
    ('dwayne', 'duane', 0.822),
    ('0ð00', '0ð00', 1)
])
def test_jaro_distance(s1, s2, distance):
    if s1 is None or s2 is None:
        with pytest.raises(TypeError):
            jaro_distance(s1, s2)
    else:
        assert pytest.approx(jaro_distance(s1, s2), 0.001) == distance


@pytest.mark.parametrize('s1, s2, similarity', [
    ('dixon', 'dicksonx', 0.813),
    ('martha', 'marhta', 0.961),
    ('dwayne', 'duane', 0.84),
    ('William', 'Williams', 0.975),
    ('', 'foo', 0),
    ('a', 'a', 1),
    ('abc', 'xyz', 0)
])
def test_jaro_winkler(s1, s2, similarity):
    if s1 is None or s2 is None:
        with pytest.raises(TypeError):
            jaro_winkler_similarity(s1, s2)
    else:
        assert pytest.approx(jaro_winkler_similarity(s1, s2), 0.001) == similarity


@pytest.mark.parametrize('vec1, vec2, similarity', [
    ([1, 2, 1, 3], [2, 5, 2, 3], 0.916),
    ([1, 2], [2, 3], 0.992)
])
def test_cosine_similarity(vec1, vec2, similarity):
    if vec1 is None or vec2 is None:
        with pytest.raises(TypeError):
            cosine_similarity(vec1, vec2)
    else:
        assert pytest.approx(cosine_similarity(vec1, vec2), 0.001) == similarity


@pytest.mark.parametrize('bag1, bag2, similarity', [
    (['a', 'b', 'c'], ['a', 'a', 'c'], 0.775),
    (['cc', 'dd', 'a'], ['dd', 'a', 'cc'], 1.0)
])
def test_string_cosine_similarity(bag1, bag2, similarity):
    if bag1 is None or bag2 is None:
        with pytest.raises(TypeError):
            string_cosine_similarity(bag1, bag2)
    else:
        assert pytest.approx(string_cosine_similarity(bag1, bag2), 0.001) == similarity


@pytest.mark.parametrize('set1, set2, similarity', [
    (set(['abc', 'bcd', 'cde']), set(['cde', 'efg', 'fgh']), 0.2),
    (set(['abc', 'def']), set(['abc', 'def']), 1.0),
    (set(['abc', 'def']), set(['hij', 'klm']), 0.0)
])
def test_jaccard_index_similarity(set1, set2, similarity):
    if set1 is None or set2 is None:
        with pytest.raises(TypeError):
            jaccard_index_similarity(set1, set2)
    else:
        assert pytest.approx(jaccard_index_similarity(set1, set2), 0.001) == similarity


@pytest.mark.parametrize('bag1, bag2, df_corpus, doc_size, math_log, score', [
    # (['a', 'b', 'a'], ['a', 'c'], [['a', 'b', 'a'], ['a', 'c'], ['a']], False, 0.1754),
    # (['a', 'b', 'a'], ['a', 'c'], [['a', 'b', 'a'], ['a', 'c'], ['a'], ['b']], True, 0.1117),
    # (['a', 'b', 'a'], ['a'], [['a', 'b', 'a'], ['a', 'c'], ['a']], False, 0.5547),
    # (['a', 'b', 'a'], ['a'], [['x', 'y'], ['w'], ['q']], False, 0.0),
    # (['a', 'b', 'a'], ['a'], [['x', 'y'], ['w'], ['q']], True, 0.0),
    # (['a', 'b', 'a'], ['a'], None, False, 0.7071)
    (['a', 'b', 'a'], ['a', 'c'], {'a': 3, 'b': 1, 'c': 1}, 3, False, 0.1754),
    (['a', 'b', 'a'], ['a', 'c'], {'a': 3, 'b': 2, 'c': 1}, 4, True, 0.1297),
    (['a', 'b', 'a'], ['a'], {'a': 3, 'b': 1, 'c': 1}, 3, False, 0.5547),
    (['a', 'b', 'a'], ['a'], {'x': 1, 'y': 1, 'w': 1, 'q': 1}, 3, False, 0.0),
    (['a', 'b', 'a'], ['a'], {'x': 1, 'y': 1, 'w': 1, 'q': 1}, 3, True, 0.0),
    (['a', 'b', 'a'], ['a'], None, 0, False, 0.7071)
])
def test_tf_idf(bag1, bag2, df_corpus, doc_size, math_log, score):
    if bag1 is None or bag2 is None or df_corpus is None:
        with pytest.raises(TypeError):
            tf_idf_similarity(bag1, bag2)
    else:
        assert pytest.approx(tf_idf_similarity(bag1, bag2, df_corpus, doc_size, math_log), 0.001) == score


def test_hybrid_jaccard_similarity():
    # use a fixed test cases here only to test hybrid jaccard itself.
    def test_function(m, n):
        if m == 'a' and n == 'p':
            return 0.7
        if m == 'a' and n == 'q':
            return 0.8
        if m == 'b' and n == 'p':
            return 0.5
        if m == 'b' and n == 'q':
            return 0.9
        if m == 'c' and n == 'p':
            return 0.2
        if m == 'c' and n == 'q':
            return 0.1

    assert pytest.approx(hybrid_jaccard_similarity(set(['a', 'b', 'c']), set(['p', 'q']), function=test_function),
                         0.001) == 0.5333


@pytest.mark.parametrize('bag1, bag2, similarity', [
    (['paul', 'johnson'], ['johson', 'paule'], 0.944),
    (['Niall'], ['Neal'], 0.805)
])
def test_monge_elkan_similarity(bag1, bag2, similarity):
    if bag1 is None or bag2 is None:
        with pytest.raises(TypeError):
            monge_elkan_similarity(bag1, bag2)
    else:
        assert pytest.approx(monge_elkan_similarity(bag1, bag2), 0.001) == similarity


@pytest.mark.parametrize('s, code', [
    ('Soundex', 'S532'),
    ('Example', 'E251'),
    ('Sownteks', 'S532'),
    ('Ekzampul', 'E251'),
    ('Euler', 'E460'),
    ('Gauss', 'G200'),
    ('Hilbert', 'H416'),
    ('Knuth', 'K530'),
    ('Lloyd', 'L300'),
    ('Lukasiewicz', 'L222'),
    ('Ellery', 'E460'),
    ('Ghosh', 'G200'),
    ('Heilbronn', 'H416'),
    ('Kant', 'K530'),
    ('Ladd', 'L300'),
    ('Lissajous', 'L222'),
    ('Wheaton', 'W350'),
    ('Burroughs', 'B620'),
    ('Burrows', 'B620'),
    ('O\'Hara', 'O600'),
    ('Washington', 'W252'),
    ('Lee', 'L000'),
    ('Gutierrez', 'G362'),
    ('Pfister', 'P236'),
    ('Jackson', 'J250'),
    ('Tymczak', 'T522'),
    ('VanDeusen', 'V532'),
    ('Ashcraft', 'A261'),
    ('Gutierrez', 'G362'),
    ('Çáŕẗéř', 'C636'),
])
def test_soundex(s, code):
    if s is None:
        with pytest.raises(ValueError):
            _soundex(s)
    if isinstance(s, int):
        with pytest.raises(TypeError):
            _soundex(s)
    else:
        assert _soundex(s) == code


@pytest.mark.parametrize('s, code', [
    ('DGIB', 'JB'),
    ('metaphone', 'MTFN'),
    ('wHErE', 'WR'),
    ('shell', 'XL'),
    ('this is a difficult string', '0S IS A TFKLT STRNK'),
    ('aeromancy', 'ERMNS'),
    ('Antidisestablishmentarianism', 'ANTTSSTBLXMNTRNSM'),
    ('sunlight labs', 'SNLT LBS'),
    ('sonlite laabz', 'SNLT LBS'),
    ('Çáŕẗéř', 'KRTR'),
    ('kentucky', 'KNTK'),
    ('KENTUCKY', 'KNTK'),
    ('NXNXNX', 'NKSNKSNKS'),
    ('Aapti', 'PT'),
    ('Aarti', 'RT'),
    ('CIAB', 'XB'),
    ('NQ', 'NK'),
    ('sian', 'XN'),
    ('gek', 'JK'),
    ('Hb', 'HB'),
    ('Bho', 'BH'),
    ('Tiavyi', 'XFY'),
    ('Xhot', 'XHT'),
    ('Xnot', 'SNT'),
    ('g', 'K'),
    ('8 queens', 'KNS'),
    ('Utah', 'UT'),
    ('WH', 'W')
])
def test_metaphone(s, code):
    if s is None:
        with pytest.raises(ValueError):
            _metaphone(s)
    if isinstance(s, int):
        with pytest.raises(TypeError):
            _metaphone(s)
    else:
        assert _metaphone(s) == code


@pytest.mark.parametrize('s, code', [
    ('Worthy', 'WARTY'),
    ('Ogata', 'OGAT'),
    ('montgomery', 'MANTGANARY'),
    ('Costales', 'CASTAL'),
    ('Tu', 'T'),
    ('martincevic', 'MARTANCAFAC'),
    ('Catherine', 'CATARAN'),
    ('Katherine', 'CATARAN'),
    ('Katerina', 'CATARAN'),
    ('Johnathan', 'JANATAN'),
    ('Jonathan', 'JANATAN'),
    ('John', 'JAN'),
    ('Teresa', 'TARAS'),
    ('Theresa', 'TARAS'),
    ('Jessica', 'JASAC'),
    ('Joshua', 'JAS'),
    ('Bosch', 'BAS'),
    ('Lapher', 'LAFAR'),
    ('wiyh', 'WY'),
    ('MacArthur', 'MCARTAR'),
    ('Pheenard', 'FANAD'),
    ('Schmittie', 'SNATY'),
    ('Knaqze', 'NAGS'),
    ('Knokno', 'NAN'),
    ('Knoko', 'NAC'),
    ('Macaw', 'MC'),
    ('T', 'T'),
    ('S', 'S'),
    ('P', 'P'),
    ('K', 'C'),
    ('M', 'M'),
    ('E', 'E')
])
def test_nysiis(s, code):
    if s is None:
        with pytest.raises(ValueError):
            _nysiis(s)
    if isinstance(s, int):
        with pytest.raises(TypeError):
            _nysiis(s)
    else:
        assert _nysiis(s) == code
