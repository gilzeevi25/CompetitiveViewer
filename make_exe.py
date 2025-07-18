import subprocess
from pathlib import Path

CMD = [
    "pyinstaller",
    "run_app.py",
    "--onedir",
    "--name",
    "NervioViz",
    "--add-data",
    "assets;assets",
    "--exclude-module",
    "tests",
    "--noconsole",
]


def main() -> None:
    subprocess.run(CMD, check=True)
    dist = Path("dist") / "NervioViz"
    if not dist.is_dir():
        raise SystemExit("Expected dist/NervioViz not found")
    print(f"Executable created in {dist}")


if __name__ == "__main__":
    main()
