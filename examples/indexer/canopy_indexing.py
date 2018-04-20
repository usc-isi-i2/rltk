import sys, os,time
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../../rltk")))
import rltk
tk = rltk.init()

s = time.time()
tparams = {'token_type': 'ngram', 'n': [3]}
fu2 = tk.get_file_iterator('../../datasets/ulan.json', type='json_line', id_path='uri[*].value')
fi1 = tk.get_file_iterator('../../datasets/npg.json', type='json_line', id_path='uri[*].value')
fi2 = fi1.copy()

print("Starting Canopy deduplication on NPG museum dataset")
tk.canopy_blocking(iter1=fi1, t1=0.8, value_path1=['name[*].value'],
 t2=0.2, similarity='jaccard', token_params=tparams, output_file_path='canopy1_npg.json' )
e = time.time()
print("Finished canopy deduplication :", e-s)

a = time.time()
print("Running Canopy record linkage on ULAN and NPG museum datasets")
tk.canopy_blocking(iter1=fi2, t1=0.8, value_path1=['name[*].value'], iter2=fu2,
 t2=0.2, value_path2=['name[*].value'], similarity='jaccard', token_params=tparams,
 output_file_path='canopy1_ulan_npg.json' )
b = time.time()
print("Finished canopy record linkage :", b-a)

