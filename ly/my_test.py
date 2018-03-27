import rltk
from rltk.similarity import *

tk = rltk.init()

it1 = tk.read_file('ex_data1.csv', type='csv', id_column='id')
it2 = tk.read_file('ex_data2.csv', type='csv', id_column='id')

for i1 in it1:
    for i2 in it2.copy():
        fv = tk.buildVector(i1, i2)
        v = fv.add_similarity_batch(levenshtein_distance)
        v = fv.add_similarity_by_attribute('v2', 'v2', levenshtein_distance)
        if fv.compute_prob() > 0.9:
            print(i1, i2)
        fv.add(0.5)

        if fv.compute_prob() > 0.9:
            print(i1, i2)

