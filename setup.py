#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='idempotent-sequence',
    version='1.0.0',
    author='Jazeps Basko',
    author_email='jazeps.basko@gmail.com',
    maintainer='Jazeps Basko',
    maintainer_email='jazeps.basko@gmail.com',
    license='MIT',
    url='https://github.com/jbasko/idempotent-sequence',
    description='Organise a set of units of code in a sequence that can be rerun repeatedly skipping already completed units',
    long_description=read('README.rst'),
    packages=['idemseq', 'idemseq.examples'],
    install_requires=['funcsigs>=1.0.2', 'werkzeug>=0.12.1'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],
)