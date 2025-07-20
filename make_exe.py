import subprocess
from pathlib import Path
import shutil

CMD = [
    "pyinstaller",
    "run_app.py",
    "--onedir",
    "--name",
    "NervioViz",
    "--exclude-module",
    "tests",
    "--noconsole",
    "--noconfirm",
    "--collect-all",
    "pandas",
    "--collect-all",
    "numpy",
]


def main() -> None:
    dist = Path("dist") / "NervioViz"
    if dist.exists():
        shutil.rmtree(dist)

    subprocess.run(CMD, check=True)

    if not dist.is_dir():
        raise SystemExit("Expected dist/NervioViz not found")
    print(f"Executable created in {dist}")


if __name__ == "__main__":
    main()
