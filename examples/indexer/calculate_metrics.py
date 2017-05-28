import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../../rltk")))
import rltk
tk = rltk.init()

ground_truth_params = {"ground_truth_file": 'base.json', "id_path": ['uri[*].value'], "value_path": ['name[*].value']}
#print tk.evaluate_indexer("linkage", 'base.json', 'result.json', 4, 4)

print tk.evaluate_indexer("linkage", '../../datasets/human_curated_results/npg.json', 'canopy1_ulan_npg.json', 187485, 12552)