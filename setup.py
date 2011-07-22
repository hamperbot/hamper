#!/usr/bin/env python2

from setuptools import setup, find_packages

from hamper import version

setup(name='hamper',
      version=version.encode('utf8'),
      description='Yet another IRC bot',
      install_requires=['pyyaml', 'Twisted'],
      author='Mike Cooper',
      author_email='mythmon@gmail.com',
      url='https://www.github.com/hamperbot/hamper',
      packages=find_packages(),
      scripts=['scripts/hamper'],
      )
