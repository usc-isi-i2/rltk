from distutils.core import setup
from setuptools import Extension
from Cython.Build import cythonize

# extensions = [
#     Extension('rltk/similarity/cython/tf_idf', ['rltk/similarity/cython/tf_idf.pyx'], language='c++', extra_compile_args=[
#         '-std=c++11'])
# ]

setup(
  name = 'rltk',
  # ext_modules = cythonize(extensions),
    ext_modules = cythonize([
        'rltk/similarity/cython/tf_idf.pyx',
        'rltk/similarity/cython/equal.pyx',
        'rltk/similarity/cython/hybrid.pyx',
        'rltk/similarity/cython/jaro.pyx',
        'rltk/similarity/cython/soundex.pyx'
    ])
)

# python setup.py build_ext --inplace