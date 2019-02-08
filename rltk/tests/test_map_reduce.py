import multiprocessing

from rltk.map_reduce import MapReduce


num_of_process = int(max(multiprocessing.cpu_count() / 4, 1))


def test_map_reduce_number():

    def mapper(x):
        return x

    def reducer(r1, r2):
        return r1 + r2

    mr = MapReduce(1, mapper, reducer)
    mr.add_task(1)
    assert mr.join() == 1

    mr = MapReduce(num_of_process, mapper, reducer)
    mr.add_task(1)
    assert mr.join() == 1

    mr = MapReduce(1, mapper, reducer)
    for i in range(1, 101):
        mr.add_task(i)
    assert mr.join() == 5050

    mr = MapReduce(num_of_process, mapper, reducer)
    for i in range(1, 101):
        mr.add_task(i)
    assert mr.join() == 5050

    mr = MapReduce(num_of_process, mapper, reducer)
    for i in range(1, 100001):
        mr.add_task(i)
    assert mr.join() == 5000050000


def test_map_reduce_object():

    def mapper(k, v):
        return {k: v}

    def reducer(r1, r2):
        for k1, v1 in r1.items():
            if k1 in r2:
                r2[k1] += v1
            else:
                r2[k1] = v1
        return r2

    mr = MapReduce(1, mapper, reducer)
    for i in range(100):
        if i % 2 == 0:
            mr.add_task('a', i)
        else:
            mr.add_task('b', i)
    assert mr.join() == {'a': 2450, 'b': 2500}

    mr = MapReduce(num_of_process, mapper, reducer)
    for i in range(100):
        if i % 2 == 0:
            mr.add_task('a', i)
        else:
            mr.add_task('b', i)
    assert mr.join() == {'a': 2450, 'b': 2500}
