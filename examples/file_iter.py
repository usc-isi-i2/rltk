import rltk

tk = rltk.init()

iter = tk.get_file_iterator('file_iter_test.txt', type='text')
for id, object in iter:
    print id, object

iter = tk.get_file_iterator('file_iter_test.jsonl', type='json_line', id_path='id_str')
for id, object in iter:
    print id, object

iter = tk.get_file_iterator('file_iter_test.csv', type='csv', id_column='id') # field_names=['newid', 'newcontent']
for id, object in iter:
    print id, object