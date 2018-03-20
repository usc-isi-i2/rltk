import sys

sys.path.append('')

from rltk import rltk

tk = rltk.init()
res = tk.levenshtein_distance('abc', 'abd')
print res

edit_distance_cost = {'insert': {'c': 50}, 'insert_default': 100, 'delete_default': 100, 'substitute_default': 100}
tk.load_edit_distance_table('A1', edit_distance_cost)  # load resource
res = tk.levenshtein_distance('a', 'abc', name='A1')

print res
