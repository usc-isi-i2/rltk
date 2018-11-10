import rltk

b1 = rltk.Block()
b1.add('001', '1', '1')
b1.add('001', '2', 'a')
b1.add('002', '1', '2')
b1.add('002', '2', 'b')
b1.add('002', '2', 'c')
print('--- block1 ---')
for bb in b1:
    print(bb)

b2 = rltk.Block()
b2.add('001', '1', '1')
b2.add('001', '2', 'a')
b2.add('001', '2', 'd')
b2.add('002', '1', '1')
b2.add('002', '2', 'c')
b2.add('002', '3', 'k')
print('--- block2 (pairwise) ---')
for bb in b2.pairwise('1', '2'):
    print(bb)
print('--- block2 (pairwise, single dataset) ---')
for bb in b2.pairwise('2'):
    print(bb)

b1_inverted = rltk.BlockingHelper.generate_inverted_indices(b1)
b2_inverted = rltk.BlockingHelper.generate_inverted_indices(b2)
b3 = rltk.BlockingHelper.union(b1, b1_inverted, b2, b2_inverted)
print('--- union ---')
for bb in b3:
    print(bb)
print('--- union raw ---')
for rr in b3.key_set_adapter:
    print(rr)

b4 = rltk.BlockingHelper.intersect(b1, b1_inverted, b2, b2_inverted)
print('--- intersect --')
for bb in b4:
    print(bb)
print('--- intersect raw --')
for rr in b4.key_set_adapter:
    print(rr)
