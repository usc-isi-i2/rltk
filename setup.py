from distutils.core import setup
from setuptools import find_packages


with open('rltk/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line)  # fetch and create __version__
            break

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    install_requires = list()
    dependency_links = list()
    for line in f:
        re = line.strip()
        if re:
            if re.startswith('git+') or re.startswith('svn+') or re.startswith('hg+'):
                dependency_links.append(re)
            else:
                install_requires.append(re)

packages = find_packages()

setup(
    name='rltk',
    version=__version__,
    packages=packages,
    url='https://github.com/usc-isi-i2/rltk',
    project_urls={
        "Bug Tracker": "https://github.com/usc-isi-i2/rltk/issues",
        "Documentation": "https://rltk.readthedocs.io",
        "Source Code": "https://github.com/usc-isi-i2/rltk",
    },
    license='MIT',
    author='USC/ISI',
    author_email='yixiangy@isi.edu',
    description='Record Linkage ToolKit',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    install_requires=install_requires,
    dependency_links=dependency_links,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology"
    )
)
