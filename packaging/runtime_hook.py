"""Add bundled binary directories to ``PATH`` at runtime."""

import importlib
import os


def _add_lib_dirs(package: str) -> None:
    """Add ``package.libs`` or ``.libs`` subdirs to ``PATH`` if present."""

    mod = importlib.import_module(package)
    base = os.path.dirname(mod.__file__)
    for name in (f"{package}.libs", ".libs"):
        libdir = os.path.join(base, name)
        if os.path.isdir(libdir):
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(libdir)
            else:  # pragma: no cover - Python < 3.8
                os.environ["PATH"] = libdir + os.pathsep + os.environ.get("PATH", "")


for pkg in ("numpy", "pandas"):
    try:
        _add_lib_dirs(pkg)
    except Exception:  # pragma: no cover - the package might not be present
        pass
