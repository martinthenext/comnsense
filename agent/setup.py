#!/usr/bin/env python
from setuptools import setup
import platform
import sys
import os

from comnsense_agent import __product__, __version__
from comnsense_agent import __author__, __author_email__

requirements = [
    'bitarray==0.8.1'
    'msgpack-python',
    'numpy==1.9.2',
    'pyzmq==14.7.0',
    'tornado',
]

if sys.version_info[0] < 3 or sys.version_info[1] < 4:
    requirements.append('enum34')


def prepare_py2exe():
    if platform.system().lower() == "windows":
        py2exe = __import__('py2exe', globals(), locals(), [], -1)
        options = {"py2exe": {
                       'includes': ['zmq.backend.cython', 'sip'],
                       'excludes': ['zmq.libzmq', '_tkinter', 'Tkinter'],
                       'dll_excludes': ['libzmq.pyd', 'msvcp90.dll']
                       }
                   }
        iconfile = os.path.join('resources', 'icon.ico')
        pngfile = os.path.join('resources', 'icon.png')
        xpmfile = os.path.join('resources', 'icon.xpm')
        import numpy
        import zmq.libzmq
        import zmq.libsodium
        data_files = [
            ('', (zmq.libzmq.__file__,
                  zmq.libsodium.__file__,)),
            ('resources', (iconfile, pngfile, xpmfile))
        ]
        windows = [{'script': 'bin/comnsense-agent'},
                   {'script': 'bin/comnsense-worker'},
                   {'script': 'bin/comnsense-tray',
                    'icon_resources': [(0, iconfile), (1, iconfile)]}]
        return dict(options=options, data_files=data_files, windows=windows)
    return {}


setup(name=__product__,
      version=__version__,
      description="Comnsense Agent",
      author=__author__,
      author_email=__author_email__,
      packages=["comnsense_agent",
                "comnsense_agent.algorithm",
                "comnsense_agent.algorithm.error_detector",
                "comnsense_agent.algorithm.header_detector",
                "comnsense_agent.algorithm.string_formatter",
                "comnsense_agent.automaton",
                "comnsense_agent.data",
                "comnsense_agent.multiplexer",
                "comnsense_agent.socket",
                "comnsense_agent.utils",
                ],
      install_requires=requirements,
      scripts=['bin/comnsense-agent',
               'bin/comnsense-worker',
               'bin/comnsense-tray'],
      license='COMMERCIAL',
      url='http://www.comnsense.io',
      classifiers=['Environment :: Console',
                   'Programming Language :: Python :: 2.7',
                   'Natural Language :: English',
                   'Development Status :: 1 - Planning',
                   'Operating System :: Unix',
                   'Operating System :: Windows',
                   'Topic :: Utilities'],
      **prepare_py2exe())
