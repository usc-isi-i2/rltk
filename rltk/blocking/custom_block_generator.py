from rltk.blocking import BlockGenerator


class CustomBlockGenerator(BlockGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'custom_function' not in self._kwargs:
            raise ValueError('Missing argument: custom_function')
        self._custom_function = self._kwargs['custom_function']

    def _generate_blocks(self):
        for r1 in self._dataset1:
            for r2 in self._dataset2:
                if self._custom_function(r1, r2):
                    self._writer.write(r1.id, r2.id)
