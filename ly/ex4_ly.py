import rltk

tk = rltk.init()

iter1 = tk.get_file_iterator('ex_data1.csv', type='csv', id_column='id')
iter2 = tk.get_file_iterator('ex_data2.csv', type='csv', id_column='id')

tk.load_feature_configuration('feature_config', 'feature_config.json')
tk.compute_labeled_features(iter1=iter1.copy(), iter2=iter2.copy(),
                    label_path='label.jsonl',
                    feature_config_name='feature_config',
                    feature_output_path='labeled_feature.jsonl')
model = tk.train_model(training_path='labeled_feature.jsonl',
                       classifier='svm') # , classifier_config={}

#tk.q_gram_blocking(iter1=iter1.copy(), iter2=iter2.copy(), ..., output_path='blocking.jsonl')
tk.compute_features(iter1=iter1.copy(), iter2=iter2.copy(),
                    feature_config_name='feature_config',
                    feature_output_path='feature.jsonl',
                    blocking_path='blocking.jsonl')
tk.predict(model, feature_path='feature.jsonl', predict_output_path='predicted.jsonl')
