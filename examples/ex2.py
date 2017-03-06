# -*- coding: utf-8 -*-

import rltk

j1 = {'id': 1, 'name': 'abc', 'gender': 'male'},
j2 = {'id': '2','name': 'bcd', 'gender': 'male'}
edit_distance_cost = {'insert': {'c':50}, 'insert_default':100, 'delete_default':100, 'substitute_default':100}

tk1 = rltk.init()
tk1.load_feature_configuration('C1', 'feature_config_1.json')
print tk1.compute_feature_vector(j1, j2, name='C1')

tk2 = rltk.init()
tk2.load_edit_distance_table('A1', edit_distance_cost)
tk2.load_feature_configuration('C1', 'feature_config_2.json')
print tk2.compute_feature_vector(j1, j2, name='C1')
