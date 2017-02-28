# -*- coding: utf-8 -*-

import rltk

edit_distance_cost = {'insert': {'c':50}, 'insert_default':100, 'delete_default':100, 'substitute_default':100}

tk = rltk.init()
tk.load_edit_distance_table('A1', edit_distance_cost)
tk.load_df_corpus('B1', 'df_corpus_1.txt', 'text', mode='append')

print tk.levenshtein_distance('a', 'abc')
print tk.levenshtein_distance('a', 'abc', name='A1')
print tk.normalized_levenshtein_distance('a', 'abc', name='A1')
print tk.tf_idf(['a', 'b', 'a'], ['a', 'c','d','f'], name='B1')