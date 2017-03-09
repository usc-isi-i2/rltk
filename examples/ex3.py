# -*- coding: utf-8 -*-

import rltk

tk = rltk.init()
tk.featurize_ground_truth('feature_file_1.jsonl', 'ground_truth_1.jsonl')
tk.featurize_ground_truth('feature_file_1.jsonl', 'ground_truth_1.jsonl', 'featurized.jsonl')
