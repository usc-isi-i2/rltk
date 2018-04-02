import rltk

b1 = rltk.BlockArrayWriter()
b1.write('1', 'a')
b1.write('2', 'b')
b1.write('2', 'c')
b1.close()
b1 = rltk.BlockArrayReader(b1.get_handler())
print('--- block1 ---')
for bb in b1:
    print(bb)

b2 = rltk.BlockArrayWriter()
b2.write('1', 'a')
b2.write('1', 'd')
b2.write('2', 'c')
b2.close()
b2 = rltk.BlockArrayReader(b2.get_handler())
print('--- block2 ---')
for bb in b2:
    print(bb)

b3 = rltk.BlockArrayWriter()
rltk.BlockingHelper(reader1=b1, reader2=b2).union(writer=b3)
b3 = rltk.BlockArrayReader(b3.get_handler())
print('--- union ---')
for bb in b3:
    print(bb)