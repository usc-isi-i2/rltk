from rltk.io.reader import Reader


class BlockReader(Reader):
    """
    Block reader.
    """

    def __next__(self):
        """
        Iterator of id pairs generated according to blocks.
        
        Returns:
            iter: id1, id2.
        """
        raise NotImplementedError
