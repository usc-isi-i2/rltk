import hashlib
from typing import List, Set

from datasketch import MinHash,  MinHashLSH

def ngram(n: int, s: str, sep: str = ' ', padded: bool = False) -> List[str]:
    """Generate sequence of n-grams from string"""
    if len(s) == 0:
        return []
    if padded:
        pad = sep * (n - 1)
        s = pad + s + pad
    s = s.split(' ')
    s = sep.join(s)
    if len(s) < n:
        return [s]
    return [s[i:i + n] for i in range(len(s) - n + 1)]

def generate_minhash_blocking_keys(
        tokens: List[str], num_perm: int, threshold: float, key_len: int = 10) -> Set[str]:
    """Generate blocking keys using MinHash Locality Sensitive Hashing"""
    m = MinHash(num_perm=num_perm)
    for d in tokens:
        m.update(d.encode('utf8'))
    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
    lsh.insert("m", m)

    keys = set()
    for hashtable in lsh.hashtables:
        byte_key = list(hashtable._dict.keys())[0]
        keys.add(hashlib.sha1(byte_key).hexdigest()[:key_len])
    return keys
