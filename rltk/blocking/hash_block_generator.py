from rltk.blocking import BlockGenerator
from rltk.blocking.inverted_index_block_generator import InvertedIndexBlockGenerator


class HashBlockGenerator(BlockGenerator):
    """
    Generate blocks based on hash function.
    
    Args:
        hash_function (Callable): The block will be generated based on the hash value returns.
                                The signature is `hash_function(r: Record) -> str`.
        hash_function1 (Callable): Specific hash function for dataset1.
        hash_function2 (Callable): Specific hash function for dataset2.
                                
    Note:
        Either `hash_function` or both `hash_function1` and `hash_function2` should be given.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hash_function = self._kwargs.get('hash_function', None)
        self._hash_function1 = self._kwargs.get('hash_function1', self._hash_function)
        self._hash_function2 = self._kwargs.get('hash_function2', self._hash_function)
        if not self._hash_function1 or not self._hash_function2:
            raise ValueError('hash_function does not set properly')
        self._inverted_index_block_generator = \
            InvertedIndexBlockGenerator(self._dataset1, self._dataset2, self._writer,
                                        tokenizer1=lambda x: [self._hash_function1(x)],
                                        tokenizer2=lambda x: [self._hash_function2(x)])

    def _generate_blocks(self):
        return self._inverted_index_block_generator._generate_blocks()
