# -*- coding: utf-8 -*-

import rltk

tk = rltk.init()
tk.featurize_ground_truth('feature_file_1.jsonl', 'ground_truth_1.jsonl')
tk.featurize_ground_truth('feature_file_1.jsonl', 'ground_truth_1.jsonl', 'featurized.jsonl')

featurized_ground_truth = [
    {'feature_vector': [0, 0], 'label': [0], 'id': [1, 2]},
    {'feature_vector': [1, 1], 'label': [1], 'id': [3, 4]}
]
model = tk.train_classifier(featurized_ground_truth, config={'function': 'svm'})
print model.predict([[2., 2.]])
