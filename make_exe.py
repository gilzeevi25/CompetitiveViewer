import subprocess
from pathlib import Path
import shutil
import os

CMD = [
    "pyinstaller",
    "run_app.py",
    "--onedir",
    "--name", "NervioViz",
    "--noconsole",
    "--noconfirm",
    "--clean",
    "--exclude-module", "tests",
    "--exclude-module", "pyqtgraph.examples",  # <-- avoids crashing hook
    "--collect-all", "pandas",
    "--collect-all", "numpy",
    "--copy-metadata", "pandas",
    "--copy-metadata", "numpy",
    "--runtime-hook", "packaging/runtime_hook.py",  # if needed by your app
    "--add-data",
    f"resources{os.pathsep}resources",
]


def main() -> None:
    dist = Path("dist") / "NervioViz"
    build = Path("build")

    if dist.exists():
        shutil.rmtree(dist)
    if build.exists():
        shutil.rmtree(build)

    subprocess.run(CMD, check=True)

    if not dist.is_dir():
        raise SystemExit("❌ Build failed: dist/NervioViz not found")
    print(f"✅ Executable created in: {dist}")


if __name__ == "__main__":
    main()
