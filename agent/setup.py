#!/usr/bin/env python
from setuptools import setup
import platform
import sys

requirements = ['pyzmq', 'tornado', 'msgpack-python']

if sys.version_info[0] < 3 or sys.version_info[1] < 4:
    requirements.append('enum34')

options = {}
data_files = []
if platform.system().lower() == "windows":
    requirements.append('pywin32')
    py2exe = __import__('py2exe', globals(), locals(), [], -1)
    options = {"py2exe": {
                   'includes': ['zmq.backend.cython'],
                   'excludes': ['zmq.libzmq'],
                   'dll_excludes': ['libzmq.pyd']
                   }
               }
    import zmq.libzmq
    import zmq.libsodium
    data_files = [
        ('', (zmq.libzmq.__file__, zmq.libsodium.__file__))
    ]

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
      options=options,
      data_files=data_files,
      windows=[{'script': 'bin/comnsense-agent'}],
      classifiers=['Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Operating System :: Windows',
                   'Topic :: Utilities'])
