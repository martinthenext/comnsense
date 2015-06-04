#!/usr/bin/env python
from setuptools import setup
import platform
import sys

requirements = ['pyzmq', 'tornado', 'msgpack-python']
if platform.system().lower() == "windows":
    requirements.append('pywin32')

if sys.version_info[0] < 3 or sys.version_info[1] < 4:
    requirements.append('enum34')

test_requirements = ['pytest', 'pytest-allure-adaptor', 'mock']

setup(name='comnsense-agent',
      version='0.0.1',
      description="Comnsense Agent",
      author='Comnsense Team',
      author_email='team@comnsense.io',
      packages=["comnsense_agent",
                "comnsense_agent.data",
                "comnsense_agent.utils"],
      install_requires=requirements,
      test_suite='tests',
      test_require=test_requirements,
      scripts=['bin/comnsense-agent'],
      license='COMERCIAL',
      url='http://comnsense.io',
      classifiers=['Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Operating System :: Windows',
                   'Topic :: Utilities'])
