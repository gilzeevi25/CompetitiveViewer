import os
import numpy as _np

_libdir = os.path.join(os.path.dirname(_np.__file__), 'numpy.libs')
if os.path.isdir(_libdir):
    if hasattr(os, 'add_dll_directory'):
        os.add_dll_directory(_libdir)
    else:
        os.environ['PATH'] = _libdir + os.pathsep + os.environ.get('PATH', '')
