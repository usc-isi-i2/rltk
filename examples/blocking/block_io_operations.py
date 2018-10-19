import rltk

ks_adapter = rltk.MemoryKeySetAdapter()
b1 = rltk.BlockWriter(ks_adapter)
b1.write('001', rltk.BlockDatasetID.Dataset1, '1')
b1.write('001', rltk.BlockDatasetID.Dataset2, 'a')
b1.write('002', rltk.BlockDatasetID.Dataset1, '2')
b1.write('002', rltk.BlockDatasetID.Dataset2, 'b')
b1.write('002', rltk.BlockDatasetID.Dataset2, 'c')
b1.close()
b1 = rltk.BlockReader(ks_adapter)
print('--- block1 ---')
for bb in b1:
    print(bb)

b2 = rltk.BlockWriter()
b2.write('001', rltk.BlockDatasetID.Dataset1, '1')
b2.write('001', rltk.BlockDatasetID.Dataset2, 'a')
b2.write('001', rltk.BlockDatasetID.Dataset2, 'd')
b2.write('002', rltk.BlockDatasetID.Dataset1, '1')
b2.write('002', rltk.BlockDatasetID.Dataset2, 'c')
b2.close()
b2 = rltk.BlockReader(b2.key_set_adapter)
print('--- block2 ---')
for bb in b2:
    print(bb)

b3 = rltk.BlockWriter()
rltk.BlockingHelper(reader1=b1, reader2=b2).union(writer=b3)
b3 = rltk.BlockReader(b3.key_set_adapter)
print('--- union ---')
for bb in b3:
    print(bb)
print('--- union raw ---')
for rr in b3.key_set_adapter:
    print(rr)