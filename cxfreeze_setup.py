from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['lxml._elementpath', 'gzip'], excludes=[], compressed=True)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('report-ng.py', base=base, icon='src/resources/icon.ico'),
    Executable('yamled.py', base=base, icon='src/resources/yamled.ico'),
]

from src.version import Version
version = Version()

setup(name='report-ng',
      version = version.version,
      description = 'report-ng-'+version.version, #version.long_title,
      author = version.c,      
      options = dict(build_exe = buildOptions),
      executables = executables)
