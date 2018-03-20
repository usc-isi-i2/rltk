import rltk

tk = rltk.init()

iter1 = tk.get_file_iterator('../../datasets/ulan.json', type='json_line', id_path='uri[*].value')
iter2 = tk.get_file_iterator('../../datasets/puam.json', type='json_line', id_path='uri[*].value')

tk.load_feature_configuration('feature_config', 'feature_config.json')
tk.compute_labeled_features(iter1=iter1.copy(), iter2=iter2.copy(),
                    label_path='labeled_100.jsonl',
                    feature_config_name='feature_config',
                    feature_output_path='labeled_feature.jsonl')
model = tk.train_model(training_path='labeled_feature.jsonl',
                       classifier='svm') # , classifier_config={}

# tk.dump_model(model, 'model.pkl')
# model = tk.load_model('model.pkl')

# tk.q_gram_blocking(
#     iter1=iter1, q1=[3], value_path1=['name[*].value'],
#     iter2=iter2, q2=[3], value_path2=['name[*].value'],
#     output_file_path='blocking.jsonl')

# head -n 100 blocking.jsonl > blocking_100.jsonl

tk.compute_features(iter1=iter1.copy(), iter2=iter2.copy(),
                    feature_config_name='feature_config',
                    feature_output_path='feature.jsonl',
                    blocking_path='blocking_100.jsonl')
tk.predict(model, feature_file='feature.jsonl', predict_output_file='predicted.jsonl')
tk.filter('predicted.jsonl', 'filtered.jsonl', unique_id1=False)
