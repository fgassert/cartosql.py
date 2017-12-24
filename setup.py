#!/usr/bin/env python
from setuptools import setup

setup(
    name='cartopy',
    version='0.1',
    description='simple library for interacting with CARTO SQL API',
    license='MIT',
    author='Francis Gassert',
    url='https://github.com/fgassert/cartopy',
    packages=['cartopy'],
    install_requires=['requests', 'docopt'],
    scripts=['csql']
)
