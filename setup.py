"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup
import sys

APP = ['tracking.py']
DATA_FILES = []
OPTIONS = {'argv_emulation': True, 'iconfile': 'src/icon.icns'}
VERSION="0.6"

if sys.platform == 'darwin':
    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        version=VERSION,
        setup_requires=['py2app'],
    )
elif sys.platform == 'linux2':
    setup(
        name='tracking',
        scripts=['tracking.py'],
        packages=['src', 'src/tissue_plot'],
        data_files=DATA_FILES,
        version=VERSION
    )
elif sys.platform == "win32":
    pass
else:
    raise RuntimeError("Platform '%s' is not supported by the install script" % sys.platform)