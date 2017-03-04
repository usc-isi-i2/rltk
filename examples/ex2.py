# -*- coding: utf-8 -*-

import rltk

tk = rltk.init()

tk.load_feature_configuration('C1', 'feature_config_1.json')
v = tk.compute_feature_vector({'name': 'abc', 'gender': 'male'}, {'name': 'bcd', 'gender': 'male'}, name='C1')
print v