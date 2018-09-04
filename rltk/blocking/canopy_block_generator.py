import json
import math
import numpy as np
import random
import itertools

from rltk.blocking import BlockGenerator


class CanopyBlockGenerator(BlockGenerator):
    """
    Canopy based block generator.

    Args:
        t1 (float): The loose distance.
        t2 (float): The tight distance.
        vectorize_function (Callable): Convert values in record to a vector. 
                                    The signature is `vectorize(r: Record) -> List`.
        distance_metric (Callable): Compute the distance between two vectors.
                                    The signature is `distance(v1: List, v2: List) -> float`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._t1 = self._kwargs.get('t1')
        self._t2 = self._kwargs.get('t2')
        self._vectorize_function = self._kwargs.get('vectorize_function')
        if self._t1 <= self._t2:
            raise ValueError('t1 should be greater than t2')
        if self._t1 <= 0 or self._t2 <= 0:
            raise ValueError('t1 and t2 should greater than 0')
        self._distance_metric = self._kwargs.get('distance_metric')

    def _generate_blocks(self):
        vec_id_mapping = {}  # map data to
        dataset = []
        for r1 in self._dataset1:
            v = self._vectorize_function(r1)
            k = self._encode_key(v)
            vec_id_mapping[k] = vec_id_mapping.get(k, [])
            vec_id_mapping[k].append((0, r1.id))  # 0 means dataset1
            dataset.append(v)
        for r2 in self._dataset2:
            v = self._vectorize_function(r2)
            k = self._encode_key(v)
            vec_id_mapping[k] = vec_id_mapping.get(k, [])
            vec_id_mapping[k].append((1, r2.id))  # 1 means dataset2
            dataset.append(v)

        clusters = self._run_canopy_clustering(dataset, self._t1, self._t2, self._distance_metric)
        for c in clusters:
            id1s, id2s = [], []
            for vec in c:
                ids = vec_id_mapping[self._encode_key(vec)]
                for ds_id, r_id in ids:
                    if ds_id == 0:
                        id1s.append(r_id)
                    else:
                        id2s.append(r_id)
            for id1, id2 in itertools.product(id1s, id2s):
                self._writer.write(id1, id2)

    @staticmethod
    def _encode_key(v):
        return json.dumps(v)

    @staticmethod
    def _run_canopy_clustering(dataset, t1, t2, distance_metric):
        """
        The algorithm proceeds as follows, using two thresholds t1 (the loose distance) and t2 (the tight distance), 
        where t1 > t2.

        1. Begin with the set of data points to be clustered.
        2. Remove a point from the set, beginning a new 'canopy' containing this point.
        3. For each point left in the set, assign it to the new canopy \
            if its distance to the first point of the canopy is less than the loose distance t1.
        4. If the distance of the point is additionally less than the tight distance t2, 
            remove it from the original set.
        5. Repeat from step 2 until there are no more data points in the set to cluster.
        """
        canopies = []
        while len(dataset) > 0:
            center_idx = random.randint(0, len(dataset) - 1)
            center_vec = dataset[center_idx]
            new_canopy = []
            delete_list = []
            del dataset[center_idx]

            for d_idx in range(len(dataset)):
                d = dataset[d_idx]
                distance = distance_metric(center_vec, d)
                if distance < t1:
                    new_canopy.append(d)
                if distance < t2:
                    delete_list.append(d_idx)

            for d_idx in sorted(delete_list, reverse=True):
                del dataset[d_idx]
            new_canopy.append(center_vec)  # add center
            canopies.append(new_canopy)
        return canopies
