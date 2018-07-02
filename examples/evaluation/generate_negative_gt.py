from construct_datasets import *

gt = rltk.GroundTruth()
gt.load('gt_positive_only.csv')


def score_function(r1, r2):
    return rltk.levenshtein_similarity(r1.data, r2.data2)

gt.generate_negatives(ds1, ds2, score_function=score_function)

for id1, id2, label in gt:
    print(id1, id2, label)
