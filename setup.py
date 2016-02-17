#!/usr/bin/env python

import os
import re
import sys
from codecs import open

from setuptools import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py register')
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload --universal')
    sys.exit()

requires = ['redis']
version = '0.0.1'

def read(f):
    return open(f, encoding='utf-8').read()

setup(
    name='records',
    version=version,
    description='Messaging Queue',
    long_description=read('README.md') + '\n\n' + read('HISTORY.md'),
    author='Mukesh Yadav',
    author_email='mukesh@ingenioustechie.com',
    url='https://github.com/ingenioustechie/rufous',
    py_modules=['rufous'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    license='ISC',
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Testing',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    )
)