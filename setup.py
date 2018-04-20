from distutils.core import setup
from setuptools import find_packages

with open('VERSION', 'r') as f:
    version = f.readline().strip()

if not version or len(version) == 0:
    exit()

setup(
    name='rltk',
    version=version,
    packages=find_packages(),
    url='https://github.com/usc-isi-i2/rltk',
    license='MIT',
    author='USC/ISI',
    author_email='',
    description='Record Linkage ToolKit'
)
