from rltk.io.writer.block_writer import BlockWriter
from rltk.dataset import Dataset


class BlockGenerator(object):
    def __init__(self, dataset1 : Dataset, dataset2 : Dataset, writer: BlockWriter):
        self._writer = writer
        self._dataset1 = dataset1
        self._dataset2 = dataset2

        self._generate()

        handler = self._writer.get_handler()
        self._writer.close()
        return handler

    def _generate(self):
        raise NotImplementedError