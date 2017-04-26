import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../rltk")))
import rltk
tk = rltk.init()

print("Running Qgram indexing on GM museum dataset")
fi1 = tk.get_file_iterator('../datasets/ima.json', type='json_line', id_path='uri[*].value')
tk.q_gram_blocking(file_iter=fi1, q=[3], value_path=['name[*].value'], output_file_path='./ima_qgrams.json' )


print("Running Qgram indexing on ULAN and GM museum datasets")
fu1 = tk.get_file_iterator('../datasets/ulan.json', type='json_line', id_path='uri[*].value')
fi2 = tk.get_file_iterator('../datasets/ima.json', type='json_line', id_path='uri[*].value')

tk.q_gram_blocking(file_iter1=fu1, q1=[3], value_path1=['name[*].value'], file_iter2=fi2, 
 q2=[3], value_path2=['name[*].value'], output_file_path='./qgram_ulan_gm.json' )

