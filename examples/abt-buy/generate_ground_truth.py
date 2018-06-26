import rltk
import random
from create_datasets import *

gt = rltk.GroundTruth()

all_matches = []
reader = rltk.CSVReader(open('../../datasets/Abt-Buy/abt_buy_perfectMapping.csv', encoding='latin-1'))
for r in reader:
    id_abt = r['idAbt']
    id_buy = r['idBuy']
    all_matches.append('{},{}'.format(id_abt, id_buy))


# 200 positives
matches = random.sample(all_matches, 200)
for m in matches:
    id_abt, id_buy = m.split(',')
    gt.add_positive(id_abt, id_buy)


# 200 negatives
all_matches_set = set(all_matches)
result = []
pairs = rltk.get_record_pairs(ds_abt, ds_buy)
for r_abt, r_buy in pairs:

    id_key = '{},{}'.format(r_abt.id, r_buy.id)
    if id_key in all_matches_set:
        continue

    jaccard_score = rltk.jaccard_index_similarity(r_abt.name_tokens, r_buy.name_tokens)
    result.append((id_key, jaccard_score))

result.sort(key=lambda v: v[1], reverse=True)
size = len(result)
for i in range(10):
    min_idx = int(size / 10) * i
    # max_idx = int(size / 10) * (i + 1) - 1
    max_idx = min_idx + 20
    selected = result[min_idx:max_idx]
    for r in selected:
        id_abt, id_buy = r[0].split(',')
        gt.add_negative(id_abt, id_buy)

gt.save('gt.csv')