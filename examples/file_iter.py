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

print '----'
iter1 = tk.get_file_iterator('file_iter_test.txt', type='text')
for id, value in iter1:
    print id, value
    break
iter2 = iter1.copy()
for id, value in iter1:
    print id, value
for id, value in iter2:
    print id, value
