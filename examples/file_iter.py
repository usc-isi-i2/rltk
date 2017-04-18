import rltk

tk = rltk.init()

iter = tk.get_file_iterator('file_iter_test.txt', type='text')
for id, value in iter:
    print id, value

iter = tk.get_file_iterator('file_iter_test.jsonl', type='json_line', id_path='id_str', value_path='content')
for id, value in iter:
    print id, value

iter = tk.get_file_iterator('file_iter_test.csv',
                            type='csv', id_column='id', value_columns=['content']) # field_names=['xx', 'yy']
for id, value in iter:
    print id, value
