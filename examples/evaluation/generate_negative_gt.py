from construct_datasets import *


print('generate negatives')
gt = rltk.GroundTruth()
gt.load('gt_positive_only.csv')


def score_function(r1, r2):
    return rltk.levenshtein_similarity(r1.name, r2.name)

gt.generate_negatives(ds1, ds2, score_function=score_function)

for id1, id2, label in gt:
    print(id1, id2, label)


print('generate all negatives')
gt1 = rltk.GroundTruth()
gt1.load('gt_positive_only.csv')

gt1.generate_all_negatives(ds1, ds2)
for id1, id2, label in gt1:
    print(id1, id2, label)


print('generate stratified negatives')
gt2 = rltk.GroundTruth()
gt2.load('gt_positive_only.csv')


num_of_cluster = 3
curr = -1


def classify(r1, f2):
    global curr
    curr = (curr + 1) % num_of_cluster
    return curr

gt2.generate_stratified_negatives(ds1, ds2, classify, num_of_cluster)
for id1, id2, label in gt2:
    print(id1, id2, label)