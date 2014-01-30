#!/usr/bin/env python2

from setuptools import setup, find_packages

from hamper import version

requires = open('requirements.txt').read().split('\n')
requires = [dep for dep in requires if 'psycopg' not in dep]

setup(
    name='hamper',
    version=version.encode('utf8'),
    description='Yet another IRC bot',
    install_requires=requires,
    author='Mike Cooper',
    author_email='mythmon@gmail.com',
    url='https://www.github.com/hamperbot/hamper',
    packages=find_packages(),
    scripts=['scripts/hamper'],
)
