import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../../rltk")))
import rltk
tk = rltk.init()

print("Running MinHash LSH indexing on IMA museum dataset")
fi1 = tk.get_file_iterator('datasets/ima.json', type='json_line', id_path='uri[*].value')
#tk.lsh_minhash_blocking(iter1=fi1, value_path1=['name[*].value'], output_file_path='ima_qgrams.json', threshold=0.5 )
tk.lsh_minhash_blocking(iter1=fi1, value_path1=['name[*].value'], output_file_path='ima_qgrams.json', bands_rows=(5,5) )
