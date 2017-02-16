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
print r.similarity(), r.distance(), '\n'

r = tk.jaro_winkler('My string', 'My tsring')
print r.similarity(), r.distance()
r = tk.jaro_winkler('My string', 'My ntrisg')
print r.similarity(), r.distance()
r = tk.jaro_winkler('My string', 'My stirng')
print r.similarity(), r.distance()
