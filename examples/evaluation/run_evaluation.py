from construct_datasets import *

saved_ground_truth_file_name = 'ground_truth.csv'
gt = rltk.GroundTruth()
gt.load(saved_ground_truth_file_name)

gt.add_ground_truth('3', '13', True)
gt.save('saved_' + saved_ground_truth_file_name)

eva = rltk.Evaluation()

for min_confidence_100 in range(0, 100):
    threshold = min_confidence_100 / 100
    trial = rltk.Trial(gt, min_confidence=0, top_k=0,
                       label='min threshold is: {}'.format(threshold), threshold=threshold)
    pairs = rltk.get_record_pairs(ds1, ds2)
    for r1, r2 in pairs:
        c = 0.3 * rltk.levenshtein_similarity(r1.name, r2.name) + 0.7 * rltk.levenshtein_similarity(r1.laptop, r2.laptop)
        p = (c >= threshold)
        trial.add_result(r1, r2, p, c)

    trial.evaluate()
    eva.add_trial(trial)

# coord = [
#     {
#         'x': 'threshold',
#         'y': 'false_positives',
#         'label': '123'
#     },
#     {
#         'x': 'threshold',
#         'y': 'true_positives',
#         'label': '456',
#         'linestyle': '--'
#     },
#     {
#         'x': 'recall',
#         'y': 'precision',
#         'label': 'pr',
#         'linestyle': '--'
#     }
# ]
# eva.plot(coord)
eva.plot_precision_recall().show()

eva.plot_roc().show()
