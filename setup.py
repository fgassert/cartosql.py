#!/usr/bin/env python
from setuptools import setup

setup(
    name='cartosql',
    version='0.1',
    description='simple library for interacting with CARTO SQL API',
    license='MIT',
    author='Francis Gassert',
    url='https://github.com/fgassert/cartosql',
    packages=['cartosql'],
    install_requires=['requests', 'docopt'],
    scripts=['csql']
)
