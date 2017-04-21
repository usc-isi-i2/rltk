import rltk

tk = rltk.init()

iter = tk.get_file_iterator('file_iter_test.txt', type='text')
for id, value in iter:
    print id, value

iter = tk.get_file_iterator('file_iter_test.jsonl', type='json_line', id_path='id_str')
for id, value in iter:
    print id, value

iter = tk.get_file_iterator('file_iter_test.csv', type='csv', id_column='id')
for id, value in iter:
    print id, value

print '----'
# iter1 = tk.get_file_iterator('file_iter_test.txt', type='text')
iter1 = tk.get_file_iterator('file_iter_test.csv', type='csv', id_column='id')
for id, value in iter1:
    print id, value
    break
iter2 = iter1.copy()
for id, value in iter1: # starts from id2
    print id, value
for id, value in iter2: # starts from id2
    print id, value
