# -*- coding: utf-8 -*-

import rltk

tk = rltk.init()
tk.load_edit_distance_table('A1', insert_default=100, delete_default=100, substitute_default=100)
print tk.levenshtein_distance('a', 'abc')
print tk.levenshtein_distance('a', 'abc', name='A1')
print tk.normalized_levenshtein_distance('a', 'abc', name='A1')