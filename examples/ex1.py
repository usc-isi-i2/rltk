import rltk

tk = rltk.init()

r = tk.levenshtein('abc', 'def')
print r.similarity(), r.distance()
r = tk.levenshtein('aaa', 'aaa')
print r.similarity(), r.distance()
r = tk.levenshtein('aaa', '')
print r.similarity(), r.distance()
r = tk.levenshtein('', '')
print r.similarity(), r.distance(), '\n'

r = tk.normalized_levenshtein('apple', 'pineapple')
print r.similarity(), r.distance()
r = tk.normalized_levenshtein('aaa', '')
print r.similarity(), r.distance()