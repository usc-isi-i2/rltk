import os
import time
import tempfile

from rltk.blocking import BlockGenerator
from rltk.io.reader import BlockFileReader
from rltk.io.writer import BlockFileWriter


class InvertedIndexBlockGenerator(BlockGenerator):
    """
    Generic inverted index based block generator.
    
    Args:
        tokenizer (Callable): The tokenizer for record from dataset1 and dataset 2.
                                The signature is `tokenizer(r: Record) -> List[str]`.
        tokenizer1 (Callable): The tokenizer for record of dataset 1.
        tokenizer2 (Callable): The tokenizer for record of dataset 2.
        buffer_size (int, optional): The maximum size of in-memory buffer, defaults to 10,000.
        token_size (int, optional): The maximum number that this token is used in documents. Defaults to 1,000.
        temp_dir_path (str, optional): Where the temp data stores while buffer is out-of-memory. 
                                        Defaults to system's temporary path (:py:meth:`tempfile.gettempdir`).
                                        
    Note:
        Either `tokenizer` or both `tokenizer1` and `tokenizer2` should be given.
        
    
    Note:
        If you use QGram as tokenizer, this becomes QGram block generator.
        
    Note:
        If tokens are pre-calculated, they can be returned directly in tokenizer function (e.g., `return r.name_tokens`).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tokenizer = self._kwargs.get('tokenizer', None)
        self._tokenizer1 = self._kwargs.get('tokenizer1', self._tokenizer)
        self._tokenizer2 = self._kwargs.get('tokenizer2', self._tokenizer)
        if not self._tokenizer1 or not self._tokenizer2:
            raise ValueError('Tokenizer is not properly set')
        self._buffer_size = self._kwargs.get('buffer_size') or 10000
        self._token_size = self._kwargs.get('token_size') or 1000
        self._temp_dir_path = self._kwargs.get('temp_dir_path', tempfile.gettempdir())

    def _generate_blocks(self):

        temp_file_prefix = os.path.join(self._temp_dir_path, str(time.time()))
        ds1_temp_filename = temp_file_prefix + '.ds1.temp'
        ds2_temp_filename = temp_file_prefix + '.ds2.temp'
        ds1_inverted_temp_filename = temp_file_prefix + '.ds1.inverted.temp'
        blacklist = set()

        # normal indices for ds1 (tokens: id), in order to complement blacklist
        ds1_temp_writer = BlockFileWriter(ds1_temp_filename, buffer_size=self._buffer_size,
                                          index_blacklist=blacklist, set_size=self._token_size)
        for r1 in self._dataset1:
            tokens = self._tokenizer1(r1)
            for t in tokens:
                ds1_temp_writer.write(t, r1.id)
        ds1_temp_writer.close()
        blacklist = ds1_temp_writer.get_blacklist()

        # inverted indices for ds1 (id: tokens)
        ds1_inverted_temp_writer = BlockFileWriter(ds1_inverted_temp_filename, buffer_size=self._buffer_size)
        for t, id1 in BlockFileReader(ds1_temp_filename):
            ds1_inverted_temp_writer.write(id1, t)
        ds1_inverted_temp_writer.close()

        # normal indices for ds2 (token: ids)
        ds2_temp_writer = BlockFileWriter(ds2_temp_filename, buffer_size=self._buffer_size,
                                          index_blacklist=blacklist, set_size=self._token_size)
        for r2 in self._dataset2:
            tokens = self._tokenizer2(r2)
            for t in tokens:
                ds2_temp_writer.write(t, r2.id)
        ds2_temp_writer.close()

        # construct blocks
        ds2_iter = iter(BlockFileReader(ds2_temp_filename))
        eof = False
        while not eof:
            # read a chunk of data from ds2 into memory
            ds2_indices = dict()
            count = self._buffer_size

            while count > 0:
                next_value = next(ds2_iter, None)
                if not next_value:
                    eof = True
                    break

                t, id2 = next_value
                if not t in ds2_indices:
                    ds2_indices[t] = set()
                ds2_indices[t] = ds2_indices[t] | set([id2])
                count -= 1

            # scan on-disk ds1 and in-memory ds2 chunk and make pairs
            ds1_inverted_temp_reader = BlockFileReader(ds1_inverted_temp_filename)
            for id1, t in ds1_inverted_temp_reader:
                if t in ds2_indices:
                    for id2 in ds2_indices[t]:
                        self._writer.write(id1, id2)

        os.remove(ds1_temp_filename)
        os.remove(ds2_temp_filename)
        os.remove(ds1_inverted_temp_filename)
