from collections import defaultdict

import rltk.utils as utils

def get_ngrams(s,n):
	return set([s[i:i+n] for i in range(len(s)-1)])

def qgram_distance(s0, s1, n=2):
	"""
	QGram Distance is the number of distinct q-grams (n-grams) between 2 strings
	
	Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: QGram Distance.

    Examples:
        >>> rltk.qgram_distance('abcde','abdcde')
        3
	"""

	s0_ngrams = get_ngrams(s0, n)
	s1_ngrams = get_ngrams(s1, n)
	all_ngrams = list(s0_ngrams | s1_ngrams)

	v0 = [1 if all_ngrams[i] in s0 else 0 for i in range(len(all_ngrams))]
	v1 = [1 if all_ngrams[i] in s1 else 0 for i in range(len(all_ngrams))]

	return sum([1 if v0[i]!=v1[i] else 0  for i in range(len(v0))])

def qgram_similarity(s0, s1, n=2):
	"""
	QGram Similarity is the number of common q-grams (n-grams) between 2 strings
	
	Args:
        s1 (str): Sequence 1.
        s2 (str): Sequence 2.

    Returns:
        float: QGram Similarity.

    Examples:
        >>> rltk.qgram_similarity('abcde','abdcde')
        3
    """

	s0_ngrams = get_ngrams(s0, n)
	s1_ngrams = get_ngrams(s1, n)
	all_ngrams = list(s0_ngrams | s1_ngrams)

	v0 = [1 if all_ngrams[i] in s0 else 0 for i in range(len(all_ngrams))]
	v1 = [1 if all_ngrams[i] in s1 else 0 for i in range(len(all_ngrams))]

	return sum([1 if v0[i]==v1[i] else 0  for i in range(len(v0))])	