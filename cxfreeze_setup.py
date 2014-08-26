from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['lxml._elementpath', 'gzip'], excludes=[], compressed=True)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('wasar.py', base=base, icon='src/resources/icon.ico')
]

from src.version import Version
version = Version()

setup(name='wasar',
      version = version.version,
      description = version.long_title,
      author = version.c,      
      options = dict(build_exe = buildOptions),
      executables = executables)
