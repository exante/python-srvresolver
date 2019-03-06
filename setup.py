#!/usr/bin/env python

import os
from distutils.util import convert_path
from setuptools import setup, find_packages

location = os.path.abspath(os.path.dirname(__file__))
with open('README.md') as readme:
    description = readme.read()
metadata = dict()
with open(convert_path('src/srvresolver/version.py')) as metadata_file:
    exec(metadata_file.read(), metadata)


setup(
    name='srvresolver',
    version=metadata['__version__'],

    description='SRV record resolver for python',
    long_description_content_type='text/markdown',
    long_description=description,

    url='https://github.com/exante/python-srvresolver',
    author='EXANTE',
    author_email='',

    license='MIT',

    keywords='dns srv resolve',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    zip_safe=False,

    install_requires=[
        'dnspython'
    ],
    extras_require={
        'postgresql resolver': ['psycopg2-binary>=2.7,<2.8']
    }
)
