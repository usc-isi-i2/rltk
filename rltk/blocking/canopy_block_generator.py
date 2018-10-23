import json
import random
from typing import Callable

from rltk.blocking import BlockGenerator
from rltk.io.adapter.key_set_adapter import KeySetAdapter
from rltk.io.writer.block_writer import BlockWriter
from rltk.blocking.block_dataset_id import BlockDatasetID


class CanopyBlockGenerator(BlockGenerator):
    """
    Canopy based block generator.
    
    Args:
        t1 (float): The loose distance.
        t2 (float): The tight distance.
        distance_metric (Callable): Compute the distance between two vectors return from :meth:`block`.
                              The signature is `distance(v1: List, v2: List) -> float`
    """
    def __init__(self, t1, t2, distance_metric):
        if t1 <= t2:
            raise ValueError('t1 should be greater than t2')
        if t2 <= 0:
            raise ValueError('t1 and t2 should greater than 0')

        self._t1 = t1
        self._t2 = t2
        self._distance_metric = distance_metric

    def block(self, dataset, function_: Callable = None, property_: str = None,
              ks_adapter: KeySetAdapter = None):
        """
        The return of `property_` or `function_` should be a vector (list).
        """
        ks_adapter = super()._block_args_check(function_, property_, ks_adapter)
        for r in dataset:
            value = function_(r) if function_ else getattr(r, property_)
            k = self._encode_key(value)
            if not isinstance(value, list):
                raise ValueError('Return of the function or property should be a vector (list)')
            ks_adapter.add(k, r.id)
        return ks_adapter

    @staticmethod
    def _encode_key(obj):
        return json.dumps(obj)

    @staticmethod
    def _decode_key(str_):
        return json.loads(str_)

    def generate(self, ks_adapter1: KeySetAdapter, ks_adapter2: KeySetAdapter, block_writer: BlockWriter = None):
        block_writer = BlockGenerator._generate_args_check(block_writer)
        dataset = []
        for key, _ in ks_adapter1:
            dataset.append(self._decode_key(key))
        for key, _ in ks_adapter2:
            dataset.append(self._decode_key(key))

        clusters = self._run_canopy_clustering(dataset, self._t1, self._t2, self._distance_metric)

        for c in clusters:
            for vec in c:
                key = self._encode_key(vec)
                set_ = ks_adapter1.get(key)
                if set_:
                    for id1 in set_:
                        block_writer.write(key, BlockDatasetID.Dataset1, id1)
                set_ = ks_adapter2.get(key)
                if set_:
                    for id2 in set_:
                        block_writer.write(key, BlockDatasetID.Dataset2, id2)
        return block_writer.key_set_adapter

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

            # delete vector from dataset from backward
            for d_idx in sorted(delete_list, reverse=True):
                del dataset[d_idx]
            new_canopy.append(center_vec)  # add center
            canopies.append(new_canopy)
        return canopies
