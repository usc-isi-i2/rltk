import rltk

tk = rltk

print tk.levenshtein_similarity('abc', 'def')
print tk.levenshtein_similarity('aaa', 'aaa')
print tk.levenshtein_similarity('aaa', '')
print tk.levenshtein_similarity('', '')

print tk.normalized_levenshtein_similarity('apple', 'pineapple')
print tk.normalized_levenshtein_similarity('aaa', '')

print tk.jaro_winkler_similarity('My string', 'My tsring')
print tk.jaro_winkler_similarity('My string', 'My ntrisg')
print tk.jaro_winkler_similarity('My string', 'My stirng')
