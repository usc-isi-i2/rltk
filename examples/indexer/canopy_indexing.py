import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../../rltk")))
import rltk
tk = rltk.init()


import cProfile


import time 
s = time.time()
tparams = {'token_type': 'ngram', 'n': [3]}

print("Running Canopy indexing on ULAN and NPG museum datasets")
fu2 = tk.get_file_iterator('../../datasets/ulan.json', type='json_line', id_path='uri[*].value')
fi1 = tk.get_file_iterator('../../datasets/npg.json', type='json_line', id_path='uri[*].value')

tk.canopy_blocking(iter1=fi1, t1=0.8, value_path1=['name[*].value'], iter2=fu2,
 t2=0.2, value_path2=['name[*].value'], similarity='jaccard', token_params=tparams,
 output_file_path='canopy1_ulan_npg.json' )


e = time.time()
print("Time :", e-s)