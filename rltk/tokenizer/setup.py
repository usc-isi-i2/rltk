#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'digCrfTokenizer',
    'description': 'digCrfTokenizer',
    'author': 'Craig Milo Rogers',
    'url': 'https://github.com/usc-isi-i2/dig-crf-tokenizer',
    'download_url': 'https://github.com/usc-isi-i2/dig-crf-tokenizer',
    'author_email': 'rogers@isi.edu',
    'license' : 'Apache License 2.0',
    'version': '0.1.6',
    'packages': ['digCrfTokenizer']
}

setup(**config)
