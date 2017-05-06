#sample python script to calculate metrics of indexer
import sys,json, os
from collections import defaultdict

def build_base_truth(ground_truth_file):
	"""
		Read the groud truth file and construct base_truth

		Args:
			ground_truth_file (string) : Ground truth json file

		Returns:
			base_truth (dict) : dict of pairs
	"""
	base_truth = defaultdict(set)
	with open(ground_truth_file) as ip:
		for line in ip:
			d = json.loads(line)
			base_truth[d["id1"]].add(d["id2"])
	return base_truth

def build_result(linking_type, blocking_file):
	"""
		Read the result file and construct blocks

		Args:
			linking_type (string) : deduplication or linkage
			blocking_file (string) : blocking result json file

		Returns:
			result (dict) : dict of blocks
	"""
	result = defaultdict(set)
	with open(blocking_file) as ip:
		for line in ip:
			d = json.loads(line)
			if linking_type=="deduplication":
				#TO-DO The format not yet fixed
				records = d.keys()
			else:
				for k in d.keys():
					result[k] |= set(d[k])
	return result

def calculate_metrics(linking_type, ground_truth_file, blocking_file, db1_size, db2_size=None):
	"""
		Calculate indexer metrics

		Args:
			linking_type (string) : database deduplication or linkage
			ground_truth_file ()
	"""
	pair_count = 0
	recall = 0
	db1_size = float(db1_size)


	base_truth = build_base_truth(ground_truth_file)
	pair_count = len(base_truth)
	result = build_result(linking_type,blocking_file)

	#calculate true positives / false positives / true negatives
	tp = 0
	fp = 0
	fn = 0

	for k,v in base_truth.items():
		if k in result:
			for i in v:
				if i in result[k]:
					tp += 1
				else:
					fn += 1
		else:
			fn += len(v)

	if db2_size is not None:
		db2_size = float(db2_size)
		total_pairs = db1_size * db2_size
		reduction_ratio = 1 - float(pair_count) / (db1_size * db2_size)
	else:
		total_pairs = (db1_size) * (db1_size - 1) / 2
		total_candidates = (db1_size) * (db1_size - 1) / 2
		reduction_ratio = 1 - float(pair_count) / total_candidates

	if (tp+fn) > 0:
		pairs_completeness = float(tp) / (tp + fn)
		pairs_quality = float(tp) / pair_count

	return reduction_ratio, pairs_completeness, pairs_quality

