import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest


@pytest.mark.slow
def test_build_and_run(tmp_path):
    if shutil.which('pyinstaller') is None:
        pytest.skip('pyinstaller not available')

    env = os.environ.copy()
    env.setdefault('QT_QPA_PLATFORM', 'offscreen')

    # build executable
    subprocess.run([sys.executable, 'make_exe.py'], check=True, env=env)

    exe = Path('dist') / 'NervioViz' / ('NervioViz.exe' if os.name == 'nt' else 'NervioViz')
    assert exe.is_file()

    # run the executable briefly to ensure it starts without crashing
    proc = subprocess.Popen([str(exe)], env=env)
    time.sleep(2)
    running = proc.poll() is None
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    assert running, f'process exited early with code {proc.returncode}'
