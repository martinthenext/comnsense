#!/usr/bin/env python
from setuptools import setup
import platform
import sys
import os

requirements = ['pyzmq', 'tornado', 'msgpack-python']

if sys.version_info[0] < 3 or sys.version_info[1] < 4:
    requirements.append('enum34')

options = {}
data_files = []
iconfile = ''
if platform.system().lower() == "windows":
    requirements.append('PyQt4')
    py2exe = __import__('py2exe', globals(), locals(), [], -1)
    options = {"py2exe": {
                   'includes': ['zmq.backend.cython', 'sip'],
                   'excludes': ['zmq.libzmq'],
                   'dll_excludes': ['libzmq.pyd', 'msvcp90.dll']
                   }
               }
    iconfile = os.path.join('resources', 'icon.ico')
    pngfile = os.path.join('resources', 'icon.png')
    xpmfile = os.path.join('resources', 'icon.xpm')
    import zmq.libzmq
    import zmq.libsodium
    data_files = [
        ('', (zmq.libzmq.__file__,
              zmq.libsodium.__file__,)),
        ('resources', (iconfile, pngfile, xpmfile))
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
      scripts=['bin/comnsense-agent',
               'bin/comnsense-worker',
               'bin/comnsense-tray'],
      license='COMERCIAL',
      url='http://comnsense.io',
      options=options,
      data_files=data_files,
      windows=[{'script': 'bin/comnsense-agent'},
               {'script': 'bin/comnsense-worker'},
               {'script': 'bin/comnsense-tray',
                'icon_resources': [(0, iconfile), (1, iconfile)]}],
      classifiers=['Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Operating System :: Windows',
                   'Topic :: Utilities'])
